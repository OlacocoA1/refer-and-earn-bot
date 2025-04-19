// server/routes/auth.js

const express = require("express");
const router = express.Router();
const axios = require("axios");
const User = require("../models/User");
const { v4: uuidv4 } = require("uuid");

// Register user and initiate payment
router.post("/register", async (req, res) => {
  try {
    const { fullName, email, phone, referredBy } = req.body;

    const existingUser = await User.findOne({ email });
    if (existingUser) return res.status(400).json({ message: "Email already registered." });

    const referralCode = uuidv4().slice(0, 8);

    const user = new User({
      fullName,
      email,
      phone,
      referralCode,
      referredBy: referredBy || null,
      paid: false,
    });

    await user.save();

    // Initialize Paystack payment
    const response = await axios.post(
      "https://api.paystack.co/transaction/initialize",
      {
        email,
        amount: 100000, // 1000 naira in kobo
        callback_url: "https://your-site-url.com/api/auth/verify", // Replace with your frontend
      },
      {
        headers: {
          Authorization: `Bearer ${process.env.PAYSTACK_SECRET_KEY}`,
          "Content-Type": "application/json",
        },
      }
    );

    return res.status(200).json({
      message: "Registration successful. Redirect to Paystack to pay.",
      paystackLink: response.data.data.authorization_url,
      userId: user._id,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Something went wrong." });
  }
});

// Verify Paystack payment
router.get("/verify", async (req, res) => {
  const { reference } = req.query;

  try {
    const response = await axios.get(`https://api.paystack.co/transaction/verify/${reference}`, {
      headers: {
        Authorization: `Bearer ${process.env.PAYSTACK_SECRET_KEY}`,
      },
    });

    const data = response.data.data;

    if (data.status !== "success") {
      return res.status(400).json({ message: "Payment failed." });
    }

    const user = await User.findOne({ email: data.customer.email });
    if (!user) return res.status(404).json({ message: "User not found." });

    if (user.paid) return res.status(400).json({ message: "User already verified." });

    user.paid = true;
    await user.save();

    // Add 300 naira bonus to referrer
    if (user.referredBy) {
      const referrer = await User.findOne({ referralCode: user.referredBy });
      if (referrer) {
        referrer.balance += 300;
        await referrer.save();
      }
    }

    res.redirect("https://your-site-url.com/payment-success"); // Redirect to frontend success page
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Verification error." });
  }
});

module.exports = router;

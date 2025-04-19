// server/routes/withdraw.js

const express = require("express");
const router = express.Router();
const axios = require("axios");
const User = require("../models/User");

// Withdraw route
router.post("/request", async (req, res) => {
  const { email, bankCode, accountNumber } = req.body;

  try {
    const user = await User.findOne({ email });

    if (!user || !user.paid) {
      return res.status(403).json({ message: "User not found or not verified" });
    }

    if (user.balance < 1000) {
      return res.status(400).json({ message: "Minimum withdrawal is ₦1000" });
    }

    // Resolve account name
    const resolve = await axios.get(
      `https://api.paystack.co/bank/resolve?account_number=${accountNumber}&bank_code=${bankCode}`,
      {
        headers: {
          Authorization: `Bearer ${process.env.PAYSTACK_SECRET_KEY}`,
        },
      }
    );

    const accountName = resolve.data.data.account_name;

    // Create transfer recipient
    const recipient = await axios.post(
      `https://api.paystack.co/transferrecipient`,
      {
        type: "nuban",
        name: accountName,
        account_number: accountNumber,
        bank_code: bankCode,
        currency: "NGN",
      },
      {
        headers: {
          Authorization: `Bearer ${process.env.PAYSTACK_SECRET_KEY}`,
          "Content-Type": "application/json",
        },
      }
    );

    const recipientCode = recipient.data.data.recipient_code;

    // Initiate transfer
    const transfer = await axios.post(
      `https://api.paystack.co/transfer`,
      {
        source: "balance",
        amount: user.balance * 100, // in kobo
        recipient: recipientCode,
        reason: "Referral earnings withdrawal",
      },
      {
        headers: {
          Authorization: `Bearer ${process.env.PAYSTACK_SECRET_KEY}`,
          "Content-Type": "application/json",
        },
      }
    );

    // Reset user balance
    user.balance = 0;
    await user.save();

    return res.json({
      message: "Withdrawal initiated successfully",
      transfer: transfer.data.data,
    });
  } catch (err) {
    console.error(err.response?.data || err);
    return res.status(500).json({ message: "Withdrawal failed. Check account info or try again later." });
  }
});

module.exports = router;

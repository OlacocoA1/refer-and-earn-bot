// server/routes/users.js

const express = require("express");
const router = express.Router();
const User = require("../models/User");

// Get balance
router.get("/balance/:email", async (req, res) => {
  try {
    const user = await User.findOne({ email: req.params.email });

    if (!user) return res.status(404).json({ message: "User not found" });

    if (!user.paid) return res.status(403).json({ message: "Payment not completed" });

    return res.json({
      balance: user.balance,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Server error" });
  }
});

// Get referral link
router.get("/referral/:email", async (req, res) => {
  try {
    const user = await User.findOne({ email: req.params.email });

    if (!user) return res.status(404).json({ message: "User not found" });

    const referralLink = `https://your-site-url.com/register?ref=${user.referralCode}`;

    return res.json({
      referralLink,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Server error" });
  }
});

module.exports = router;

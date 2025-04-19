// server/models/User.js

const mongoose = require("mongoose");

const userSchema = new mongoose.Schema({
  fullName: {
    type: String,
    required: true,
  },

  email: {
    type: String,
    required: true,
    unique: true,
  },

  phone: {
    type: String,
    required: true,
    unique: true,
  },

  paid: {
    type: Boolean,
    default: false,
  },

  balance: {
    type: Number,
    default: 0,
  },

  referralCode: {
    type: String,
    required: true,
    unique: true,
  },

  referredBy: {
    type: String, // This will hold the referral code of the referrer
    default: null,
  },

  createdAt: {
    type: Date,
    default: Date.now,
  },
});

module.exports = mongoose.model("User", userSchema);

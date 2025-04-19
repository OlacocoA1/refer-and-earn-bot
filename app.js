// server/app.js

const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const mongoose = require("mongoose"); // if using MongoDB
const authRoutes = require("./routes/auth");
const userRoutes = require("./routes/users");
const withdrawRoutes = require("./routes/withdraw");

dotenv.config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Connect to DB
require("./db")();

// Routes
app.use("/api/auth", authRoutes);
app.use("/api/users", userRoutes);
app.use("/api/withdraw", withdrawRoutes);

// Default Route
app.get("/", (req, res) => {
  res.send("ReferNaira backend is live!");
});

// Port
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

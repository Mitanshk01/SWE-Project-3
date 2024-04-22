const express = require('express');
const router = express.Router();

// Import controllers
const {
  registerUser,
  authenticateUser,
  getUser,
} = require('../controllers/users');

// Register route
router.post('/register', registerUser);

// Login route
router.post('/login', authenticateUser);

// User route
router.get('/', getUser);

module.exports = router;
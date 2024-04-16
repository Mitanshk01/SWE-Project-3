const User = require('../models/User');
const jwt = require('jsonwebtoken');

const handleErrors = (err) => {
    let errors = { username: '', password: '' };

    if (err.code === 11000) {
        errors.username = 'That username is already registered';
        return errors;
    }

    if (err.message.includes('User validation failed')) {
        Object.values(err.errors).forEach(({ properties }) => {
            errors[properties.path] = properties.message;
        });
    }

    return errors;
};

const createToken = (id) => {
    return jwt.sign({ id }, 'secret', {
        expiresIn: '1d'
    });
};

exports.register = async (req, res) => {
    const { username, password } = req.body;
    console.log("Registering user")
    console.log(username, password);
    try {
        const user = await User.create({ username, password });
        const token = createToken(user._id);
        res.status(201).json({ user: user._id, token });
    } catch (err) {
        const errors = handleErrors(err);
        res.status(400).json({ errors });
    }
};

exports.login = async (req, res) => {
    const { username, password } = req.body;

    try {
        const user = await User.findOne({ username });
        if (user && await user.comparePassword(password)) {
            const token = createToken(user._id);
            res.status(200).json({ user: user._id, token });
        } else {
            res.status(401).json({ error: 'Incorrect username or password' });
        }
    } catch (err) {
        res.status(401).json({ error: 'Incorrect username or password' });
    }
};
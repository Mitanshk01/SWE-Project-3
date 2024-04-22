const express = require("express");
const app = express();
const http = require("http");
const server = http.createServer(app);
const bodyParser = require("body-parser");
const cors = require("cors");
const mongoose = require("mongoose");
require("dotenv").config();

const PORT = 4003;

app.use(cors({
  origin: 'http://localhost:3000' // Adjust this to match your frontend URL if different
}));

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

const DB =
  "mongodb+srv://swayamagrawal:rkcvMxl2OYhj0Qb0@cluster0.eihouhl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";

mongoose
  .connect(DB, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then((con) => {
    console.log("DB Connection Successful!");
  });

const connection = mongoose.connection;
connection.once("open", function () {
  console.log("MongoDB database connection established successfully");
});

// const UserRouter = require("./routes/users");
// app.use("/user", UserRouter);

const authRoutes = require('./routes/authRoutes');
app.use('/auth', authRoutes);

server.listen(PORT, () => {
  console.log(`Backend app listening at http://localhost:${PORT}`);
});
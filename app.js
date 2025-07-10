const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const app = express();
const port = 3000;

app.use(express.static('/public'));

app.use(express.urlencoded({ extended: true }));

const db = new sqlite3.Database('users.db'); // Connect to the SQLite database

// Create a table for user registration if it doesn't exist
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstName TEXT,
    lastName TEXT,
    email TEXT,
    password TEXT
  )`);
});

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});

app.post('/register', (req, res) => {
  const firstName = req.body.firstName;
  const lastName = req.body.lastName;
  const email = req.body.email;
  const password = req.body.password;

  // Insert user registration data into the database
  const stmt = db.prepare('INSERT INTO users (firstName, lastName, email, password) VALUES (?, ?, ?, ?)');
  stmt.run(firstName, lastName, email, password);
  stmt.finalize();

  res.send('Registration successful');

  // For demonstration purposes, you can redirect to another page after successful registration
  res.redirect('/login-page-laptop.html');
});

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});

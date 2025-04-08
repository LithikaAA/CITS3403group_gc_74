```markdown
# 🎵 VibeShare

**VibeShare** is a web-based music data sharing platform that allows users to upload their Spotify listening history, visualise their music preferences, and selectively share insights with friends. Whether you're comparing your favourite tracks or discovering new genres through your social circle, VibeShare helps you explore music in a more connected and engaging way.

## 🚀 Features

- **🔐 User Authentication**  
  Secure sign-up and log-in functionality using Flask-Login.

- **📁 Data Upload**  
  Upload your Spotify listening history via exported data from Spotify or publicly available Kaggle datasets.

- **📊 Data Visualisation**  
  Explore your top artists, tracks, genres, and listening trends through dynamic and interactive charts.

- **🤝 Data Sharing**  
  Share your data with specific users and explore data that others have shared with you.

- **📈 Personal Dashboard**  
  Track listening durations, genre preferences, time-of-day habits, and more in a personalised view.

- **🌐 Friendship Network**  
  Connect with other users to exchange music tastes and discover what your friends are listening to.

---

## 🧱 Tech Stack

| Layer        | Technology                    |
|--------------|-------------------------------|
| Frontend     | HTML, CSS, Bootstrap, JavaScript |
| Backend      | Python (Flask)                |
| Database     | SQLite with SQLAlchemy ORM    |
| Authentication | Flask-Login                 |
| Visualisation | Chart.js / JavaScript-based libraries |

---

## 📂 Project Structure

```
vibeshare/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── upload.py
│   │   ├── share.py
│   ├── templates/
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── dashboard.html
│   │   ├── upload.html
│   │   ├── share.html
│   ├── static/
│   │   ├── css/style.css
│   │   ├── js/app.js
│   │   ├── img/logo.png
├── tests/
│   └── test_app.py
├── deliverables/
├── run.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ Setup Instructions

To run the application locally:

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/vibeshare.git
   cd vibeshare
   ```

2. **Set up a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   python run.py
   ```

5. **Access the app**

   Open your browser and go to: `http://127.0.0.1:5000`

---

## 🧪 Testing Instructions

To run the test suite:

```bash
pytest
```

This includes:

- ✅ Unit tests in `tests/`
- ✅ Selenium tests (ensure the server is running)

---

## 👥 Group Members

| UWA ID   | Name                   | GitHub Username  |
|----------|------------------------|------------------|
| 23614901 | Kylan Gillmore         | xxx       |
| 23864782 | Adrian Gonsalves       | Adundo123        |
| 23812347 | Lithika Senthil Kumar  | LithikaAA        |
| 23666908 | Zi Qian Tan            | Squirtl3-Nee     |

---

## 📌 Notes

- Do **not** commit the virtual environment folder (`venv/`) or local database files.
- Use GitHub Issues and Pull Requests to manage project tasks, bugs, and collaboration.
- Passwords are stored securely using salted hashes.
- All forms are protected with CSRF tokens.
- Environment variables should be stored in `.env` and never committed to version control.

---

## 📜 License

This project is developed as part of the [UWA CSSE] curriculum. For academic use only.
```

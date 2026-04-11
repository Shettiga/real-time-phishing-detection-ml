from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from src.feature_extraction import extract_features
from backend.db import users_collection
import sqlite3

app = Flask(__name__)
CORS(app)

# Load ML model
model = joblib.load("phishing_model.pkl")

# ------------------ HOME ------------------
@app.route("/")
def home():
    return "PhishGuard Backend Running"

# ------------------ PREDICT ------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    url = data["url"]

    features = extract_features(url)
    prediction = model.predict([features])[0]

    result = "Phishing Website" if prediction == 1 else "Safe Website"

    return jsonify({"prediction": result})

# ------------------ REGISTER ------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # ✅ FIXED KEYS
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    phone = data.get("phone")
    dob = data.get("dob")
    password = data.get("password")

    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                email TEXT UNIQUE,
                phone TEXT,
                dob TEXT,
                password TEXT
            )
        """)

        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, phone, dob, password)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, email, phone, dob, password))

        conn.commit()
        conn.close()

        return jsonify({"message": "User registered successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ------------------ LOGIN ------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cursor.fetchone()

    conn.close()

    if user:
        return jsonify({
            "message": "Login successful",
            "user_id": user[0],  # ID
            "name": user[1]      # first_name
        })
    else:
        return jsonify({"error": "Invalid email or password"}), 401
# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(debug=True)
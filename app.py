from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from src.feature_extraction import extract_features
from backend.db import users_collection
import sqlite3
from pymongo import MongoClient
from backend.db import history_collection

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

    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    phone = data.get("phone")
    dob = data.get("dob")
    password = data.get("password")

    # 🔥 Check if user exists
    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already exists"}), 400

    # Insert into MongoDB
    users_collection.insert_one({
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "dob": dob,
        "password": password
    })

    return jsonify({"message": "User registered successfully"})

# ------------------ LOGIN ------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = users_collection.find_one({
        "email": email,
        "password": password
    })

    if user:
        return jsonify({
            "message": "Login successful",
            "user_id": str(user["_id"]),
            "name": user["first_name"]
        })
    else:
        return jsonify({"error": "Invalid email or password"}), 401
    
# ------------------ SAVE SCAN ------------------
@app.route("/save_scan", methods=["POST"])
def save_scan():
    data = request.get_json()

    history_collection.insert_one({
        "user_id": data.get("user_id"),
        "url": data.get("url"),
        "result": data.get("result")
    })

    return jsonify({"message": "Saved"})

# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(debug=True)
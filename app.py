from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from src.feature_extraction import extract_features
from backend.db import users_collection

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

    email = data["email"]

    # Check if user already exists
    if users_collection.find_one({"email": email}):
        return jsonify({"message": "User already exists"}), 400

    user = {
        "firstName": data["firstName"],
        "lastName": data["lastName"],
        "email": email,
        "phone": data["phone"],
        "password": data["password"]
    }

    users_collection.insert_one(user)

    return jsonify({"message": "Registration successful"})

# ------------------ LOGIN ------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    user = users_collection.find_one({
        "email": data["email"],
        "password": data["password"]
    })

    if user:
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from src.feature_extraction import extract_features
from backend.db import users_collection, history_collection
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
import random

app = Flask(__name__)
CORS(app)

# ------------------ GLOBAL OTP STORAGE ------------------
otp_storage = {}

# ------------------ LOAD MODEL ------------------
model = joblib.load("phishing_model.pkl")

# ------------------ TWILIO SETUP ------------------
account_sid = "YOUR_TWILIO_SID"
auth_token = "YOUR_TWILIO_AUTH_TOKEN"
client = Client(account_sid, auth_token)

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

# ------------------ SEND EMAIL OTP ------------------
def send_email_otp(email, otp):
    sender = "your_email@gmail.com"
    password = "your_app_password"

    msg = MIMEText(f"Your OTP is {otp}")
    msg["Subject"] = "OTP Verification"
    msg["From"] = sender
    msg["To"] = email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.send_message(msg)
    server.quit()

# ------------------ SEND SMS OTP ------------------
def send_sms_otp(phone, otp):
    client.messages.create(
        body=f"Your OTP is {otp}",
        from_="+1234567890",
        to=phone
    )

# ------------------ SEND OTP API ------------------
@app.route("/send_otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    email = data.get("email")
    phone = data.get("phone")

    if not email or not phone:
        return jsonify({"error": "Email and phone required"}), 400

    otp = str(random.randint(100000, 999999))

    # store OTP
    otp_storage[email] = otp

    # send OTP
    send_sms_otp(phone, otp)
    send_email_otp(email, otp)

    return jsonify({"message": "OTP sent successfully"})

# ------------------ SEND WELCOME ------------------
def send_welcome_sms(phone):
    client.messages.create(
        body="🎉 Registered successfully in PhishGuard!",
        from_="+1234567890",
        to=phone
    )

def send_welcome_email(email):
    sender = "your_email@gmail.com"
    password = "your_app_password"

    msg = MIMEText("🎉 You have successfully registered in PhishGuard!")
    msg["Subject"] = "Welcome to PhishGuard"
    msg["From"] = sender
    msg["To"] = email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.send_message(msg)
    server.quit()

# ------------------ REGISTER ------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    email = data.get("email")
    user_otp = data.get("otp")

    # OTP verification
    if otp_storage.get(email) != user_otp:
        return jsonify({"error": "Invalid OTP"}), 400

    # check existing user
    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already exists"}), 400

    # save user
    users_collection.insert_one({
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "email": email,
        "phone": data.get("phone"),
        "dob": data.get("dob"),
        "password": data.get("password")
    })

    # remove OTP
    otp_storage.pop(email, None)

    # send confirmation
    send_welcome_sms(data.get("phone"))
    send_welcome_email(email)

    return jsonify({"message": "User registered successfully"})

# ------------------ LOGIN ------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    user = users_collection.find_one({
        "email": data.get("email"),
        "password": data.get("password")
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
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
from src.feature_extraction import extract_features
from backend.db import users_collection, history_collection
import smtplib
from email.mime.text import MIMEText
import random
import bcrypt
from urllib.parse import urlparse

try:
    from twilio.rest import Client
except Exception:
    Client = None

app = Flask(__name__)
CORS(app)

# ------------------ GLOBAL OTP STORAGE ------------------
otp_storage = {}

# ------------------ LOAD ML MODEL ------------------
model = joblib.load("phishing_model.pkl")


def _normalize_url(url):
    candidate = (url or "").strip()
    if not candidate:
        return ""
    if not candidate.startswith(("http://", "https://")):
        candidate = "http://" + candidate
    return candidate


def _is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)


def _is_phishing_prediction(prediction_value):
    classes = set(model.classes_.tolist()) if hasattr(model, "classes_") else set()

    # Dataset format typically uses {-1, 1}: -1 phishing, 1 legitimate.
    if classes == {-1, 1}:
        return int(prediction_value) == -1

    # Common binary format {0, 1}: 1 phishing.
    if classes == {0, 1}:
        return int(prediction_value) == 1

    # Fallback for unknown label encodings.
    return str(prediction_value).strip().lower() in {"1", "phishing", "malicious", "true"}

# ------------------ EMAIL CONFIG ------------------
EMAIL_SENDER = "sudarshan.i.shettigar@gmail.com"
EMAIL_PASSWORD = "bzwrjjpkjpycbzbd"

# ------------------ TWILIO CONFIG ------------------
ACCOUNT_SID = "your_sid"
AUTH_TOKEN = "your_token"
TWILIO_PHONE = "+1234567890"

client = Client(ACCOUNT_SID, AUTH_TOKEN) if Client else None

# ------------------ HOME ------------------
@app.route("/")
def home():
    return "PhishGuard Backend Running 🚀"

# ------------------ PREDICT ------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    url = _normalize_url(data.get("url"))

    if not _is_valid_url(url):
        return jsonify({"error": "Invalid URL format"}), 400

    features = extract_features(url)
    if not features:
        return jsonify({"error": "Unable to extract URL features"}), 400

    prediction = model.predict([features])[0]

    result = "Phishing Website" if _is_phishing_prediction(prediction) else "Safe Website"
    return jsonify({"prediction": result, "normalized_url": url})

# ------------------ SEND EMAIL OTP ------------------
def send_email_otp(email, otp):
    msg = MIMEText(f"Your OTP is: {otp}")
    msg["Subject"] = "PhishGuard OTP Verification"
    msg["From"] = EMAIL_SENDER
    msg["To"] = email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

# ------------------ SEND SMS OTP ------------------
def send_sms_otp(phone, otp):
    if client is None:
        return

    client.messages.create(
        body=f"Your PhishGuard OTP is: {otp}",
        from_=TWILIO_PHONE,
        to=phone
    )

# ------------------ SEND OTP API ------------------
@app.route("/send_otp", methods=["POST"])
def send_otp():
    try:
        data = request.get_json()

        print("Incoming Data:", data)  # 🔥 DEBUG

        email = data.get("email")
        phone = data.get("phone")

        if not email or not phone:
            return jsonify({"error": "Email and phone required"}), 400

        otp = str(random.randint(100000, 999999))
        otp_storage[email] = otp

        print("OTP:", otp)

        # ❌ TEMP disable external services
        send_email_otp(email, otp)
        send_sms_otp(phone, otp)

        return jsonify({"message": "OTP generated", "otp": otp})

    except Exception as e:
        print("ERROR:", str(e))   # 🔥 VERY IMPORTANT
        return jsonify({"error": str(e)}), 500
# ------------------ SEND WELCOME ------------------
def send_welcome_sms(phone):
    if client is None:
        return

    client.messages.create(
        body="🎉 You are successfully registered in PhishGuard!",
        from_=TWILIO_PHONE,
        to=phone
    )

def send_welcome_email(email):
    msg = MIMEText("🎉 Welcome to PhishGuard! Your registration is successful.")
    msg["Subject"] = "Welcome to PhishGuard"
    msg["From"] = EMAIL_SENDER
    msg["To"] = email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

# ------------------ REGISTER ------------------
@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        print("REGISTER DATA:", data)   # 🔥 DEBUG

        email = data.get("email")
        user_otp = data.get("otp")
        password = data.get("password")

        print("Stored OTP:", otp_storage.get(email))
        print("User OTP:", user_otp)

        # Check OTP
        if otp_storage.get(email) != user_otp:
            return jsonify({"error": "Invalid OTP"}), 400

        if users_collection.find_one({"email": email}):
            return jsonify({"error": "Email already exists"}), 400

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        users_collection.insert_one({
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "email": email,
            "phone": data.get("phone"),
            "dob": data.get("dob"),
            "password": hashed_password
        })

        otp_storage.pop(email, None)

        return jsonify({"message": "User registered successfully"})

    except Exception as e:
        print("REGISTER ERROR:", str(e))   # 🔥 IMPORTANT
        return jsonify({"error": str(e)}), 500

# ------------------ LOGIN ------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = users_collection.find_one({"email": email})

    if user and bcrypt.checkpw(password.encode(), user["password"]):
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
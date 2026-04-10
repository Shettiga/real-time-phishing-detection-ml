from flask import Flask, request, jsonify
import joblib
from src.feature_extraction import extract_features
from flask_cors import CORS

app = Flask(__name__)
CORS(app)   # ✅ CORRECT PLACE (top, after app creation)

# Load model
model = joblib.load("phishing_model.pkl")

@app.route("/")
def home():
    return "Phishing Detection API Running!"

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    url = data["url"]

    features = extract_features(url)

    prediction = model.predict([features])[0]

    result = "Phishing Website" if prediction == 1 else "Safe Website"

    return jsonify({"prediction": result})

if __name__ == "__main__":
    app.run(debug=True)
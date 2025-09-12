from flask import Flask, request, jsonify
import joblib
import re
import os

app = Flask(__name__)

# --- Load model and vectorizer ---
BASE_DIR = os.path.dirname(__file__)
model = joblib.load(os.path.join(BASE_DIR, "scam_classifier.joblib"))
vectorizer = joblib.load(os.path.join(BASE_DIR, "tfidf_vectorizer.joblib"))

# --- Text cleaning ---
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s.,!?]", "", text)
    return text.strip()

# --- Health check route (for browser GET) ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "✅ Scam Detection API is running"}), 200

# --- Prediction route (for POST) ---
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)  # parse incoming JSON
        message = data.get("text", "")

        if not message:
            return jsonify({"error": "No text provided"}), 400

        # Preprocess
        clean = clean_text(message)
        vec = vectorizer.transform([clean])

        # Prediction
        pred = model.predict(vec)[0]
        prob = model.predict_proba(vec)[0][pred]
        result = "SCAM 🚨" if pred == 1 else "LEGIT ✅"

        return jsonify({
            "prediction": result,
            "confidence": float(prob)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

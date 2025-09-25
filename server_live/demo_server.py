from flask import Flask, request, jsonify
import joblib
import re
import os
import numpy as np
from scipy.sparse import hstack

app = Flask(__name__)

# --- Load model, vectorizer, and keywords ---
BASE_DIR = os.path.dirname(__file__)
<<<<<<< Updated upstream
model = joblib.load(os.path.join(BASE_DIR, "scam_classifier.joblib"))
vectorizer = joblib.load(os.path.join(BASE_DIR, "tfidf_vectorizer.joblib"))
=======
model = joblib.load(os.path.join(BASE_DIR, "scam_classifier_xgb_hybrid.joblib"))
vectorizer = joblib.load(os.path.join(BASE_DIR, "vectorizer.joblib"))
keywords = joblib.load(os.path.join(BASE_DIR, "keywords.joblib"))
>>>>>>> Stashed changes

# --- Text cleaning ---
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s.,!?]", "", text)
    return text.strip()

# --- Helper: keyword feature extractor ---
def keyword_features(text, keywords):
    return np.array([[1 if kw in text.lower() else 0 for kw in keywords]])

# --- Health check route ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "✅ Scam Detection API is running"}), 200

# --- Prediction route ---
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)  # parse incoming JSON
        message = data.get("text", "")

        if not message:
            return jsonify({"error": "No text provided"}), 400

        # Preprocess
        clean = clean_text(message)

        # TF-IDF + Keywords
        features_tfidf = vectorizer.transform([clean])
        features_keywords = keyword_features(clean, keywords)
        features = hstack([features_tfidf, features_keywords])

        # Prediction
        pred = model.predict(features)[0]
        proba = model.predict_proba(features)[0][pred]

        label_map = {0: "LEGIT ✅", 1: "SCAM 🚨"}
        result = label_map.get(int(pred), str(pred))

        return jsonify({
            "text": message,
            "prediction": result,
            "confidence": float(proba)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

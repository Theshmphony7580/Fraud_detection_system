from flask import Flask, request, jsonify
import joblib
import re
import os
import numpy as np
from scipy.sparse import hstack
import google.generativeai as genai

app = Flask(__name__)

# --- Load model, vectorizer, and keywords ---
BASE_DIR = os.path.dirname(__file__)
model = joblib.load(os.path.join(BASE_DIR, "scam_classifier_xgb_hybrid.joblib"))
vectorizer = joblib.load(os.path.join(BASE_DIR, "vectorizer.joblib"))
keywords = joblib.load(os.path.join(BASE_DIR, "keywords.joblib"))

genai.configure(api_key="YOUR_GEMINI_API_KEY")
gemini = genai.GenerativeModel("gemini-2.5-flash")


# --- Text cleaning ---
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s.,!?]", "", text)
    return text.strip()

# --- Helper: keyword feature extractor ---
def keyword_features(text, keywords):
    return np.array([[1 if kw in text.lower() else 0 for kw in keywords]])


#---------------Gemini API Layer----------------#
def hybrid_predict(message):
    clean = clean_text(message)

    # Local prediction
    features_tfidf = vectorizer.transform([clean])
    features_keywords = keyword_features(clean, keywords)
    features = hstack([features_tfidf, features_keywords])

    pred = model.predict(features)[0]
    proba = model.predict_proba(features)[0][pred]
    label_map = {0: "LEGIT ✅", 1: "SCAM 🚨"}
    result = label_map.get(int(pred), str(pred))

    prompt = f"""
    You are a cybersecurity assistant. Classify the following message as either
    SCAM or LEGIT, and explain in one line why you think so.

    Message:
    "{message}"      and the verify the prediction made by the local model which is "{result}".
    Provide your answer in the format: "<Prediction> because <Reasoning>"  and return only SCAM or LEGIT as prediction.
    Do not mention the local model's prediction in your reasoning.
    """

    gemini_response = gemini.generate_content(prompt)
    reasoning = gemini_response.text.strip()

    return {
    "text": message,
    "prediction": reasoning,
    # "source": "Gemini Layer 🤖"
    }


    
    # Gemini fallback if uncertain
    if proba < 0.9:
        prompt = f"""
        You are a cybersecurity assistant. Classify the following message as either
        SCAM or LEGIT, and explain in one line why you think so.

        Message:
        "{message}"
        """
        try:
            gemini_response = gemini.generate_content(prompt)
            reasoning = gemini_response.text.strip()
            return {
                "text": message,
                "prediction": reasoning,
                "source": "Gemini Layer 🤖"
            }
        except Exception as e:
            return {
                "text": message,
                "prediction": result,
                "confidence": float(proba),
                "source": f"Local Model (Gemini error: {str(e)})"
            }

    return {
        "text": message,
        "prediction": result,
        "confidence": float(proba),
        "source": "Local Model ⚙️"
    }


# --- Health check route ---
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "✅ Scam Detection API is running"}), 200

# --- Prediction route ---
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        message = data.get("text", "")

        if not message:
            return jsonify({"error": "No text provided"}), 400

        # Use the hybrid_predict function for prediction (Gemini + local model)
        result = hybrid_predict(message)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

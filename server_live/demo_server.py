from flask import Flask, request, jsonify
import joblib
import re
import os
import numpy as np
from scipy.sparse import hstack
from dotenv import load_dotenv
import google.generativeai as genai
import json

# ------------------------------
# Flask app initialization
# ------------------------------
app = Flask(__name__)

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ Missing GEMINI_API_KEY in .env file")

genai.configure(api_key=api_key)
gemini = genai.GenerativeModel("gemini-2.5-pro")

# ------------------------------
# Load local ML components
# ------------------------------
BASE_DIR = os.path.dirname(__file__)
model = joblib.load(os.path.join(BASE_DIR, "scam_classifier_xgb_hybrid.joblib"))
vectorizer = joblib.load(os.path.join(BASE_DIR, "vectorizer.joblib"))
keywords = joblib.load(os.path.join(BASE_DIR, "keywords.joblib"))

# ------------------------------
# Utility functions
# ------------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s.,!?]", "", text)
    return text.strip()

def keyword_features(text, keywords):
    return np.array([[1 if kw in text.lower() else 0 for kw in keywords]])

# ------------------------------
# Gemini + Local Model Hybrid Logic
# ------------------------------
def hybrid_predict(message):
    clean = clean_text(message)

    # --- Local model: signal generation ---
    features_tfidf = vectorizer.transform([clean])
    features_keywords = keyword_features(clean, keywords)
    features = hstack([features_tfidf, features_keywords])

    pred = model.predict(features)[0]
    proba = model.predict_proba(features)[0][pred]
    local_result = "SCAM 🚨" if pred == 1 else "LEGIT ✅"

    # --- Context feature extraction ---
    contains_link = int(bool(re.search(r"http[s]?://", message)))
    contains_money = int(bool(re.search(r"\$|\d+\s?(rs|usd|dollar|rupees|reward|amount)", message.lower())))
    contains_urgency = int(bool(re.search(r"(urgent|immediately|verify|click|limited|act now)", message.lower())))
    contains_brand = int(bool(re.search(r"(amazon|netflix|paypal|bank|flipkart|google|apple)", message.lower())))

    meta_summary = (
        f"Features detected → Link: {contains_link}, Money terms: {contains_money}, "
        f"Urgency: {contains_urgency}, Brand mention: {contains_brand}."
    )

    # --- Gemini Reasoning Layer ---
    prompt = f"""
    You are an advanced cybersecurity AI assistant integrated into a real-time text safety system.

    Analyze the following text or title and classify it as one of:
    - **SCAM** → deceptive, manipulative, fraudulent, clickbait, phishing, or money-stealing attempt
    - **LEGIT** → authentic, safe, or normal communication.

    The text may come from: YouTube titles, emails, SMS, popups, or websites.
    Contextual cues: {meta_summary}
    The local ML model suggests: "{local_result}" (confidence {proba:.2f}).

    Your job:
    1. Verify if the local model’s prediction is correct.
    2. If you disagree, override it.
    3. Respond only with your reasoning and classification.

    Return only JSON (no extra text, no code block):

    {{
        "prediction": "SCAM" or "LEGIT",
        "reason": "<short reasoning based on tone, intent, or pattern>"
    }}
    """

    try:
        gemini_response = gemini.generate_content(prompt)
        response_text = gemini_response.text.strip()

        # --- Parse Gemini output safely ---
        try:
            parsed = json.loads(response_text)
            gemini_pred = parsed.get("prediction", "").upper()
            reason = parsed.get("reason", "")
        except json.JSONDecodeError:
            reason = f"Gemini returned unstructured response: {response_text}"
            gemini_pred = "UNKNOWN"

        # --- Final output ---
        return {
            "text": message,
            "gemini_prediction": gemini_pred + (" 🚨" if gemini_pred == "SCAM" else " ✅"),
            "reason": reason,
            "local_model_hint": local_result,
            "local_confidence": float(proba)
        }

    except Exception as e:
        return {
            "text": message,
            "error": str(e),
            "local_model_hint": local_result,
            "local_confidence": float(proba)
        }

# ------------------------------
# Routes
# ------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "✅ Scam Detection API is running with Gemini 2.5 Pro"}), 200

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        message = data.get("text", "")
        if not message:
            return jsonify({"error": "No text provided"}), 400

        result = hybrid_predict(message)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------------
# Entry point
# ------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

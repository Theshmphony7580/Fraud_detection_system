import json
from flask import Flask, request, jsonify
import joblib
import re
import os
import numpy as np
from scipy.sparse import hstack
from dotenv import load_dotenv
import google.generativeai as genai

app = Flask(__name__)

# --- Load model, vectorizer, and keywords ---
BASE_DIR = os.path.dirname(__file__)
model = joblib.load(os.path.join(BASE_DIR, "scam_classifier_xgb_hybrid.joblib"))
vectorizer = joblib.load(os.path.join(BASE_DIR, "vectorizer.joblib"))
keywords = joblib.load(os.path.join(BASE_DIR, "keywords.joblib"))

load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini with the API key
genai.configure(api_key=api_key)

# Create the model
gemini = genai.GenerativeModel("gemini-2.0-flash")  

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
    You are an advanced cybersecurity AI assistant integrated into a real-time text safety system.

    Task:
    Analyze the following message or title and classify it as one of:
    - **SCAM** → deceptive, manipulative, fraudulent, clickbait, phishing, or money-stealing attempt
    - **LEGIT** → authentic, normal, safe, or contextually trustworthy

    The message may come from any source (e.g., video title, email, SMS, website, chatbot). 
    Base your decision purely on *intent and behavioral cues*.

    Important Guidelines:
    - Default to "LEGIT" **unless there are clear, explicit signs of scam-like behavior.**
    - Do **not** label something as SCAM just because it sounds promotional or exaggerated.
    - Consider something SCAM **only if** it shows intent to deceive, impersonate, pressure, or steal.

    Message:
    \"\"\"{message}\"\"\"

    Local ML model prediction: "{result}"

    Your job:
    1. Evaluate if the local model’s prediction seems correct.
    2. If you disagree, override it **only with clear justification.**
    3. Briefly justify your classification with one clear reason (e.g., urgency, impersonation, or normal tone).

    Respond ONLY in strict JSON:
    {{
    "prediction": "SCAM" or "LEGIT",
    "reason": "<one-line reason>"
    }}
    """



    response = gemini.generate_content(prompt)
    text_output = response.text.strip()

    # Try to parse JSON safely
    try:
        parsed = json.loads(text_output)
    except json.JSONDecodeError:
        parsed = {
            "prediction": result,
            "reason": f"Gemini returned unstructured response: {text_output[:80]}..."
        }

    # Merge results (optional override rule)
    final_pred = parsed.get("prediction", result)
    reason = parsed.get("reason", "No reasoning provided.")

    return {
        "text": message,
        # "local_model_prediction": result,
        "gemini_prediction": final_pred,
        "reason": reason,
        # "local_confidence": float(proba)
    }


    
    # # Gemini fallback if uncertain
    # if proba < 0.9:
    #     prompt = f"""
    #     You are a cybersecurity assistant. Classify the following message as either
    #     SCAM or LEGIT, and explain in one line why you think so.

    #     Message:
    #     "{message}"
    #     """
    #     try:
    #         gemini_response = gemini.generate_content(prompt)
    #         reasoning = gemini_response.text.strip()
    #         return {
    #             "text": message,
    #             "prediction": reasoning,
    #             "source": "Gemini Layer 🤖"
    #         }
    #     except Exception as e:
    #         return {
    #             "text": message,
    #             "prediction": result,
    #             "confidence": float(proba),
    #             "source": f"Local Model (Gemini error: {str(e)})"
    #         }

    # return {
    #     "text": message,
    #     "prediction": result,
    #     "confidence": float(proba),
    #     "source": "Local Model ⚙️"
    # }


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

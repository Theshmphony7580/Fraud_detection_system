import joblib
import numpy as np
from scipy.sparse import hstack

# Load components
model = joblib.load("model\scam_classifier_xgb_hybrid_balanced.joblib")
vectorizer = joblib.load("model\\vectorizer.joblib")
keywords = joblib.load("model\\keywords.joblib")

def predict_message(message):
    # TF-IDF
    features_tfidf = vectorizer.transform([message])

    # Keywords
    features_keywords = np.array([[1 if kw in message.lower() else 0 for kw in keywords]])

    # Combine
    features = hstack([features_tfidf, features_keywords])

    # Predict
    prediction = model.predict(features)[0]
    proba = model.predict_proba(features)[0]

    label_map = {0: "Legit", 1: "Scam"}
    return {
        "text": message,
        "prediction": label_map.get(int(prediction), str(prediction)),
        "confidence": float(np.max(proba))
    }

if __name__ == "__main__":
    msg = "Happy Birthday!"
    print("="*50)
    print(f"Prediction: {predict_message(msg)['prediction']}")
    print(f"Confidence: {predict_message(msg)['confidence']}")
    print("-"*50)

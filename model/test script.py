import joblib
import numpy as np

# Load components
model = joblib.load("model/scam_classifier_lr.joblib")
vectorizer = joblib.load("model/vectorizer_lr.joblib")

def predict_message(message):
    # TF-IDF features only
    features_tfidf = vectorizer.transform([message])

    # Predict
    prediction = model.predict(features_tfidf)[0]
    proba = model.predict_proba(features_tfidf)[0]

    label_map = {0: "Legit", 1: "Scam"}
    return {
        "text": message,
        "prediction": label_map.get(int(prediction), str(prediction)),
        "confidence": float(np.max(proba))
    }

if __name__ == "__main__":
    msg = "470744 is OTP for Aadhaar (XX0708) (valid for 10 mins) at NIC. Aadhaar paperless eKYC can be used as offline verif. visit uidai.gov.in -UIDAI"
    result = predict_message(msg)
    print("="*50)
    print(f"Message: {result['text']}")
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {result['confidence']:.4f}")
    print("-"*50)

import joblib

# Load model + vectorizer
model = joblib.load("scam_classifier.joblib")

vectorizer = joblib.load("tfidf_vectorizer.joblib")
# New text
sample_text = ["your appointment is confirmed for tomorrow at 10 AM"]
sample_tfidf = vectorizer.transform(sample_text)

prediction = model.predict(sample_tfidf)
print("Prediction:", "Scam" if prediction[0] == 1 else "Legit")
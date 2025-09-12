import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# 1. Load baseline dataset
df = pd.read_csv("synthetic_scam_dataset_clean.csv")

# Features and labels
X = df["Message"]
y = df["ScamLabel"]

# 2. Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 3. Vectorization (TF-IDF)
vectorizer = TfidfVectorizer(ngram_range=(1,2), max_features=5000)  
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# 4. Model training (Logistic Regression)
model = LogisticRegression(max_iter=1000)
model.fit(X_train_tfidf, y_train)

# 5. Predictions
y_pred = model.predict(X_test_tfidf)

# 6. Evaluation
print("✅ Test Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

import joblib

# Save the trained model and vectorizer
joblib.dump(model, "scam_classifier.joblib")
joblib.dump(vectorizer, "tfidf_vectorizer.joblib")
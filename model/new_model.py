import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Load processed dataset
df = pd.read_csv("Processed_dataset.csv")

# Features and labels
X = df["message"]
y = df["encoding"]



# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=7440,
    ngram_range=(1, 2)
)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train Logistic Regression Model
model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
model.fit(X_train_vec, y_train)


# Predictions
y_pred = model.predict(X_test_vec)

# Evaluation
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}\n")

print("Classification Report:")
print(classification_report(
    y_test, y_pred,
    target_names=["Legit", "Scam"]
))

# Save model
joblib.dump(model, "scam_classifier.joblib")
joblib.dump(vectorizer, "vectorizer.joblib")
print("✅ Model saved as scam_classifier.joblib")
print("✅ Vectorizer saved as vectorizer.joblib")

# (Optional) Save test split for future validation
X_test.to_csv("X_test.csv", index=False)
y_test.to_csv("y_test.csv", index=False)
print("✅ Test split saved as X_test.csv and y_test.csv")

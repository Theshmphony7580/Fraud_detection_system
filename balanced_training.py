import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

# 1. Load dataset
df = pd.read_csv("synthetic_scam_dataset_clean.csv")

X = df["Message"]
y = df["ScamLabel"]

# 2. TF-IDF Features
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1,3),
    stop_words="english"
)
X_tfidf = vectorizer.fit_transform(X)

# 3. Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X_tfidf, y, test_size=0.2, random_state=42, stratify=y
)

# 4. Train Logistic Regression with class weight balancing
model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",  # handles imbalance
    solver="liblinear"        # good for sparse data like TF-IDF
)
model.fit(X_train, y_train)

# 5. Evaluate
y_pred = model.predict(X_test)
print("✅ Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

# 6. Save model + vectorizer
joblib.dump(model, "scam_classifier_lr.joblib")
joblib.dump(vectorizer, "vectorizer_lr.joblib")
print("✅ Logistic Regression model + vectorizer saved!")

import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

# --- 1. Load Dataset ---
df = pd.read_csv("synthetic_scam_dataset_clean.csv")

# Features and labels
X = df["text_clean"]
y = df["label"]

# --- 2. Train/Test Split ---
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# --- 3. TF-IDF Vectorization (expanded features) ---
vectorizer = TfidfVectorizer(
    max_features=20000,   # more features than before
    ngram_range=(1, 3),   # unigrams, bigrams, trigrams
    stop_words="english"
)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# --- 4. Logistic Regression with balancing ---
base_model = LogisticRegression(max_iter=3000, class_weight="balanced")

# --- 5. Cross-validation for baseline ---
cv_scores = cross_val_score(base_model, X_train_tfidf, y_train, cv=5, scoring="accuracy")
print("CV Accuracy (baseline):", cv_scores.mean())

# --- 6. Hyperparameter Tuning ---
params = {
    "C": [0.01, 0.1, 1, 10],
    "penalty": ["l2"],  # try 'l1' if you switch solver
}
grid = GridSearchCV(base_model, param_grid=params, cv=5, scoring="accuracy", n_jobs=-1)
grid.fit(X_train_tfidf, y_train)

print("Best Params:", grid.best_params_)
print("Best CV Score:", grid.best_score_)

# --- 7. Train Final Model with Best Params ---
model = grid.best_estimator_
model.fit(X_train_tfidf, y_train)

# --- 8. Evaluate on Test Set ---
y_pred = model.predict(X_test_tfidf)
print("\n✅ Test Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

# --- 9. Save Model + Vectorizer ---
joblib.dump(model, "scam_classifier_model.pkl")
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")
print("\n💾 Model & Vectorizer saved as scam_classifier_model.pkl, tfidf_vectorizer.pkl")

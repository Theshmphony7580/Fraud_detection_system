import pandas as pd
import re

# Load the dataset provided by user
df = pd.read_csv("/mnt/data/synthetic_scam_dataset_clean.csv")

# Scammy keywords list
scam_keywords = [
    "urgent", "immediately", "act now", "final warning", "account will be blocked",
    "transfer money", "wire funds", "send payment", "bitcoin", "gift card", "otp",
    "password", "cvv", "bank account", "aadhaar", "pan card", "irs", "law enforcement",
    "tech support", "you won", "lottery", "claim your prize", "account compromised",
    "unauthorized access", "legal action", "keep this secret", "don’t tell your bank", "trust me"
]

# Function to check if a keyword is present
def contains_keyword(text):
    text = str(text).lower()
    return 1 if any(re.search(r"\b" + re.escape(kw) + r"\b", text) for kw in scam_keywords) else 0

# Insert the new column right after the "text" column (if exists)
if "text" in df.columns:
    col_index = df.columns.get_loc("text") + 1
    df.insert(col_index, "keyword_flag", df["text"].apply(contains_keyword))
elif "text_clean" in df.columns:
    col_index = df.columns.get_loc("text_clean") + 1
    df.insert(col_index, "keyword_flag", df["text_clean"].apply(contains_keyword))
else:
    raise ValueError("No 'text' or 'text_clean' column found in dataset.")

# Save the updated dataset
output_path = "/mnt/data/synthetic_scam_dataset_with_keyword.csv"
df.to_csv(output_path, index=False)

output_path, df.head()

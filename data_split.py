import pandas as pd

df = pd.read_csv("synthetic_scam_dataset_clean.csv")

# Count actual samples per class
print(df["ScamLabel"].value_counts())

# Percentage distribution
print(df["ScamLabel"].value_counts(normalize=True) * 100)

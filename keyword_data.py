import google.generativeai as genai
import csv
import time
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-lite")

# Seed categories & starter keywords
scam_seeds = {
    "urgency": ["urgent", "immediately", "act now", "final warning", "limited time"],
    "payment": ["transfer money", "wire funds", "send payment", "bitcoin", "gift card"],
    "otp_info": ["otp", "password", "cvv", "bank account", "aadhaar", "pan card"],
    "authority": ["bank security team", "law enforcement", "IRS", "tech support"],
    "lottery": ["you won", "lottery", "sweepstakes", "claim your prize"],
    "threat": ["account compromised", "unauthorized access", "legal action", "penalty"],
    "social": ["keep this secret", "don’t tell your bank", "trust me"],
    "romance": ["true love", "online dating", "send money for ticket"],
    "jobs": ["easy job", "work from home", "earn daily income"],
    "crypto": ["guaranteed returns", "double your money", "crypto scheme"]
}

# Deduplication helper
def clean_variations(text):
    lines = [l.strip("-•1234567890. ").lower() for l in text.split("\n") if l.strip()]
    return list(set(lines))  # remove duplicates

# Output file
with open("scam_keywords_dataset.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["category", "base_keyword", "variation", "example_usage"])

    for category, words in scam_seeds.items():
        for word in words:
            variations = set()

            # Keep generating until we hit 20+
            while len(variations) < 20:
                prompt = f"""
                Generate 20 different scam-related variations or synonyms of the keyword "{word}".
                Along with each, provide a short scam-style example usage (10 words or less).
                Format strictly as: variation : example
                Do not repeat earlier ones.
                """
                try:
                    resp = model.generate_content(prompt)
                    if resp.text:
                        new_vars = clean_variations(resp.text)
                        for v in new_vars:
                            if ":" in v:
                                kw, ex = v.split(":", 1)
                                kw, ex = kw.strip(), ex.strip()
                                if kw not in variations:
                                    variations.add(kw)
                                    writer.writerow([category, word, kw, ex])
                except Exception as e:
                    print(f"⚠️ Error with keyword '{word}':", e)

                time.sleep(1)  # avoid API hammering

            print(f"✅ Collected {len(variations)} variations for '{word}' in category '{category}'")

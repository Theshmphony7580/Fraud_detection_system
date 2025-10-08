import google.generativeai as genai
import csv
import time
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-lite")

# Legit seed categories
legit_seeds = {
    "greetings": ["hello", "good morning", "see you soon", "take care", "happy birthday"],
    "reminders": ["meeting", "schedule", "tomorrow", "weekend", "holiday", "appointment"],
    "work_study": ["project", "assignment", "deadline", "exam", "notes", "office"],
    "family_friends": ["mom", "dad", "brother", "sister", "friend", "party"],
    "transactions": ["salary", "grocery", "bill paid", "order confirmed", "receipt"]
}

# Deduplication helper
def clean_variations(text):
    lines = [l.strip("-•1234567890. ").lower() for l in text.split("\n") if l.strip()]
    return list(set(lines))

# Output file
with open("legit_keywords_dataset.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["category", "base_keyword", "variation", "example_usage"])

    for category, words in legit_seeds.items():
        for word in words:
            variations = set()
            while len(variations) < 50:  # at least 50 per base word
                prompt = f"""
                Generate 20 natural, non-scam variations of the phrase "{word}".
                Along with each, provide a short friendly/legit usage example (10 words or less).
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
                    print(f"⚠️ Error with legit keyword '{word}':", e)

                time.sleep(1)

            print(f"✅ Collected {len(variations)} variations for legit keyword '{word}'")

import os
import random
import time
import pandas as pd
import google.generativeai as genai

genai.configure(api_key="AIzaSyC6KGYEjodS57iSNo241zD9KqzyAYSjV_c")

# model = genai.GenerativeModel("gemini-2.5-pro")



# UPDATED MODEL NAME
MODEL_NAME = "gemini-2.5-pro" 
NUM_EXAMPLES = 2000 # START WITH A VERY SMALL NUMBER TO TEST COST!
OUTPUT_FILENAME = f"api_generated_dataset_pro_1{NUM_EXAMPLES}.csv"

# --- Generation Logic ---

model = genai.GenerativeModel(MODEL_NAME)

# Define the schema and distribution
distribution = {
    'scam': 0.4,
    'legit': 0.3,
    'general': 0.3
}
sub_categories = {
    'scam': ['phishing', 'urgency', 'giveaway', 'financial', 'impersonation'],
    'legit': ['transactional', 'account_management', 'notification', 'marketing'],
    'general': ['informational', 'conversational', 'opinion', 'question']
}

dataset = []
print(f"Starting dataset generation for {NUM_EXAMPLES} examples using the '{MODEL_NAME}' model.")
print("!!! WARNING: This model is more expensive than Flash. Monitor your API usage. !!!")

for i in range(NUM_EXAMPLES):
    # Choose a category based on the desired distribution
    primary_label = random.choices(list(distribution.keys()), weights=list(distribution.values()), k=1)[0]
    secondary_label = random.choice(sub_categories[primary_label])

    # --- Create a detailed prompt for the AI ---
    prompt = f"""
    You are a data generator for a machine learning model.
    Your task is to create a single, realistic text message example.
    The example must fit the following categories:
    - Primary Category: "{primary_label}"
    - Secondary Category: "{secondary_label}"

    RULES:
    - The text should be a short, single line, like a text message, comment, or notification.
    - Do NOT include the labels in your response.
    - Just provide the raw text message.
    - Make the text sound natural and realistic. For scams, be creative.

    Example for scam/phishing: "URGENT: Your bank account has been locked. Please verify your identity at fakelink.com/verify"
    Example for legit/transactional: "Your Zomato order #12345 has been delivered."
    Example for general/conversational: "Hey, did you watch the cricket match last night?"

    Now, generate a new example.
    """

    try:
        # --- Make the API Call ---
        response = model.generate_content(prompt)
        generated_text = response.text.strip().replace("\n", "").replace('"', '')

        if generated_text:
            dataset.append([generated_text, primary_label, secondary_label])
            print(f"({i + 1}/{NUM_EXAMPLES}) Generated [{primary_label}/{secondary_label}]: {generated_text[:60]}...")
        else:
            print(f"({i + 1}/{NUM_EXAMPLES}) Failed to generate text, received empty response.")

        # --- Rate Limiting ---
        # Be a good citizen and avoid overwhelming the API.
        time.sleep(1) 

    except Exception as e:
        print(f"({i + 1}/{NUM_EXAMPLES}) An error occurred: {e}")
        # Wait longer if an error occurs
        time.sleep(5)

# --- Save to CSV ---
if dataset:
    df = pd.DataFrame(dataset, columns=['text', 'primary_label', 'secondary_label'])
    df.to_csv(OUTPUT_FILENAME, index=False)
    print(f"\n✅ Successfully generated a dataset with {len(df)} examples.")
    print(f"✅ Saved to '{OUTPUT_FILENAME}'")
else:
    print("\n❌ No data was generated. The dataset file was not created.")
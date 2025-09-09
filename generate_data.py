import requests
import pandas as pd

# --- Configuration ---
SERVER_URL = "http://127.0.0.1:5000/generate"
OUTPUT_FILE = "scam_conversations.csv"
NUM_SAMPLES_PER_SCENARIO = 5 # Generate 5 examples for each scenario

# --- Define Your Personas and Scenarios ---
PERSONA_SCAMMER = "A persuasive and friendly-sounding individual who creates a strong sense of urgency. They are skilled at deflecting questions and redirecting the conversation towards their goal."
PERSONA_VICTIM = "A slightly cautious but ultimately trusting individual who is worried about their finances and wants to resolve issues quickly."

SCENARIOS = [
    "A fake investment opportunity promising guaranteed high returns on a new cryptocurrency that doesn't exist.",
    "A call pretending to be from the victim's bank, claiming their account has been compromised and they must verify their details immediately to secure it.",
    "A text message about a package delivery failure, which requires clicking a link and paying a small 'redelivery fee' with a credit card.",
    "A social media message from a 'friend' whose account was hacked, claiming they are in an emergency abroad and need money transferred immediately.",
    "An email offering a massive discount on a popular tech product, leading to a fake e-commerce site designed to steal payment information."
]

# --- Generation Logic ---
def generate_dataset():
    """Calls the local server to generate data and saves it to a CSV."""
    all_conversations = []
    
    print("Starting dataset generation...")
    
    for i, scenario in enumerate(SCENARIOS):
        print(f"Generating for Scenario {i+1}/{len(SCENARIOS)}: '{scenario[:40]}...'")
        for j in range(NUM_SAMPLES_PER_SCENARIO):
            payload = {
                "persona_scammer": PERSONA_SCAMMER,
                "persona_victim": PERSONA_VICTIM,
                "scenario": scenario
            }
            
            try:
                response = requests.post(SERVER_URL, json=payload)
                if response.status_code == 200:
                    conversation = response.json().get('conversation')
                    all_conversations.append({
                        "text": conversation,
                        "label": 1 # 1 for scam
                    })
                    print(f"  - Sample {j+1} generated successfully.")
                else:
                    print(f"  - Error generating sample {j+1}: {response.text}")
            except requests.exceptions.ConnectionError as e:
                print("\nError: Could not connect to the server.")
                print("Please make sure the 'generator_server.py' is running in a separate terminal.")
                return

    # --- Save to CSV ---
    df = pd.DataFrame(all_conversations)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ Generation complete! Dataset saved to '{OUTPUT_FILE}'")

if __name__ == '__main__':
    generate_dataset()
import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# --- Configuration ---
# Load the API key from the .env file
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the Flask app and the Generative Model
app = Flask(__name__)
# Use a fast and free model like Gemini 2.0 Flash Lite
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash-lite-001")

# --- The Master Prompt Template (No changes here) ---
MASTER_PROMPT_TEMPLATE = """
You are a data generator. Your task is to create a realistic conversation script for a social engineering scam.

**Persona 1 (The Scammer):** {persona_scammer}
**Persona 2 (The Victim):** {persona_victim}
**Scenario:** {scenario}

Generate a back-and-forth conversation of at least 10 turns.
The conversation must be formatted as a single block of text.
"""

# --- API Endpoint for Generation ---
@app.route('/generate', methods=['POST'])
def generate_conversation():
    """Receives personas and a scenario, returns a generated conversation."""
    data = request.json
    
    if not all(key in data for key in ['persona_scammer', 'persona_victim', 'scenario']):
        return jsonify({"error": "Missing persona_scammer, persona_victim, or scenario"}), 400

    prompt = MASTER_PROMPT_TEMPLATE.format(
        persona_scammer=data['persona_scammer'],
        persona_victim=data['persona_victim'],
        scenario=data['scenario']
    )

    try:
        # Make the call to the Gemini API
        response = model.generate_content(prompt)
        
        # Extract the generated text
        generated_text = response.text
        return jsonify({"conversation": generated_text})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Run the Server ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
import openai   # optional, used only if PROVIDER=openai
import sys
import traceback

load_dotenv()

app = Flask(__name__, static_folder=None)
CORS(app)

# --- Configuration via environment variables ---
PROVIDER = os.getenv("PROVIDER", "mock").lower()  # choose: openai | groq | hf | mock
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "tiiuae/falcon-7b-instruct")  # change as needed

# If OpenAI provider selected, ensure openai package is set up correctly
if PROVIDER == "openai":
    if not OPENAI_API_KEY:
        print("WARNING: PROVIDER=openai but OPENAI_API_KEY not set.", file=sys.stderr)
    else:
        try:
            openai.api_key = OPENAI_API_KEY
        except Exception:
            pass

# --- Helper provider functions ---

def provider_mock(user_message):
    """Simple offline fallback for testing. Keeps it deterministic."""
    user = user_message.lower()
    if "hello" in user or "hi" in user:
        return "Hello! I'm the MPGU Assistant (mock). Try asking about courses, tutors, or admission."
    if "mpgu" in user:
        return ("MPGU (Moscow Pedagogical State University) is a prominent pedagogical university in Russia "
                "with strong teacher-training and education programs.")
    return ("(mock) I can't reach an AI provider right now. To enable full AI responses, set PROVIDER to "
            "'openai', 'hf' (Hugging Face), or 'groq' and provide the corresponding API key in .env.")

def provider_openai(user_message):
    """Call OpenAI (if available). Uses ChatCompletion style if openai package present."""
    try:
        messages = [
            {"role": "system", "content": "You are MPGU Smart Assistant — helpful to students and teachers at MPGU."},
            {"role": "user", "content": user_message}
        ]
        # Use ChatCompletion (works for openai package versions that support it)
        res = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, temperature=0.7)
        return res['choices'][0]['message']['content'].strip()
    except Exception as e:
        traceback.print_exc()
        return f"OpenAI error: {str(e)}"

def provider_groq(user_message):
    """Call Groq's OpenAI-compatible endpoint. Requires GROQ_API_KEY."""
    if not GROQ_API_KEY:
        return "Groq API key not configured. Set GROQ_API_KEY in .env."
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are MPGU Smart Assistant — helpful to students and teachers at MPGU."},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code != 200:
            return f"Groq API error: {r.status_code} - {r.text}"
        data = r.json()
        # handle OpenAI-compatible response structure
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        traceback.print_exc()
        return f"Groq request exception: {str(e)}"

def provider_hf(user_message):
    """Call Hugging Face Inference API. Requires HUGGINGFACE_API_KEY and model."""
    if not HUGGINGFACE_API_KEY:
        return "Hugging Face API key not configured. Set HUGGINGFACE_API_KEY in .env."

    hf_url = f"https://api-inference.huggingface.co/models/{HUGGINGFACE_MODEL}"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    # For chat-style, many HF models expect a single prompt; we concatenate system + user
    prompt = "You are MPGU Smart Assistant — helpful to students and teachers at MPGU.\n\nUser: " + user_message + "\nAssistant:"
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 256, "temperature": 0.7}}
    try:
        r = requests.post(hf_url, headers=headers, json=payload, timeout=60)
        if r.status_code != 200:
            return f"HuggingFace error: {r.status_code} - {r.text}"
        data = r.json()
        # HF sometimes returns list or dict with 'generated_text'
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"].strip()
        if isinstance(data, list) and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        if isinstance(data, dict) and isinstance(data.get("outputs"), list):
            return data["outputs"][0].get("generated_text", "").strip()
        # fallback: try string
        if isinstance(data, str):
            return data.strip()
        return f"HuggingFace unknown response: {data}"
    except Exception as e:
        traceback.print_exc()
        return f"HuggingFace request exception: {str(e)}"

# --- Flask routes ---

@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(force=True, silent=True)
    if not payload or "message" not in payload:
        return jsonify({"reply": "Invalid request. Please send JSON with a 'message' field."}), 400

    user_message = payload.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "Please type a message."}), 400

    # Choose provider
    if PROVIDER == "openai":
        reply = provider_openai(user_message)
    elif PROVIDER == "groq":
        reply = provider_groq(user_message)
    elif PROVIDER == "hf":
        reply = provider_hf(user_message)
    else:  # mock or unknown provider
        reply = provider_mock(user_message)

    return jsonify({"reply": reply})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "provider": PROVIDER})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("Starting Flask app on port", port, "- provider:", PROVIDER)
    app.run(host="0.0.0.0", port=port, debug=True)

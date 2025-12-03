import os
import requests
import json
import time  # <--- NEW: For timing
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

# 1. LOAD KEYS
load_dotenv()
MURF_KEY = os.getenv("MURF_API_KEY")
DEEPGRAM_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

if not os.path.exists('static'):
    os.makedirs('static')

# --- AI FUNCTIONS ---

def transcribe_audio_file(file_path):
    url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true"
    try:
        with open(file_path, 'rb') as f:
            audio_data = f.read()
    except Exception as e:
        return ""
    
    headers = {"Authorization": f"Token {DEEPGRAM_KEY}", "Content-Type": "audio/webm"}
    
    try:
        response = requests.post(url, headers=headers, data=audio_data, timeout=300)
        if response.status_code == 200:
            data = response.json()
            if 'results' in data:
                return data['results']['channels'][0]['alternatives'][0]['transcript']
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
    return ""

def get_therapist_response(text):
    client = Groq(api_key=GROQ_KEY)
    system_prompt = (
        "You are Serenity, an Emotional Consultant. "
        "Keep your answers EXTREMELY BRIEF (under 20 words). " # <--- NEW LIMIT
        "Validate, then ask a question."
    )
    try:
        chat = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            model="llama-3.1-8b-instant", # <--- FASTEST MODEL
            temperature=0.8,
        )
        return chat.choices[0].message.content
    except Exception as e:
        return "I'm listening."

def generate_speech(text):
    url = "https://api.murf.ai/v1/speech/generate"
    headers = {"Content-Type": "application/json", "Accept": "application/json", "api-key": MURF_KEY}
    
    payload = {
        "voiceId": "en-US-alina",
        "style": "Conversational",
        "text": text,
        "rate": 0,
        "pitch": 0,
        "sampleRate": 24000, 
        "format": "MP3", 
        "channelType": "MONO"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if "audioFile" in data:
            return data["audioFile"] 
        return None
    except Exception as e:
        return None

# --- WEB ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_greeting', methods=['GET'])
def get_greeting():
    greeting_text = "Hello Sujay. I am Serenity."
    audio_url = generate_speech(greeting_text)
    if audio_url:
        return jsonify({"text": greeting_text, "audio_url": audio_url})
    else:
        return jsonify({"error": "Failed"}), 500

@app.route('/process_audio', methods=['POST'])
def process_audio():
    # --- START TIMER ---
    start_total = time.time()
    print("\n------------------------------------------------")
    print("⏱️  STARTING PROCESS...")
    
    if 'audio_data' not in request.files:
        return jsonify({"error": "No audio file"}), 400

    # 1. UPLOAD TIME
    t0 = time.time()
    audio_file = request.files['audio_data']
    input_path = os.path.join("static", "user_input.webm")
    audio_file.save(input_path)
    t1 = time.time()
    print(f"📦 Upload & Save:    {round(t1 - t0, 2)}s") # How long browser took to send
    
    # 2. TRANSCRIBE TIME
    user_text = transcribe_audio_file(input_path)
    if not user_text: return jsonify({"error": "No speech detected"}), 400
    t2 = time.time()
    print(f"👂 Deepgram (Ears):  {round(t2 - t1, 2)}s")
    print(f"   (User said: {user_text})")
    
    # 3. THINK TIME
    ai_reply = get_therapist_response(user_text)
    t3 = time.time()
    print(f"🧠 Groq (Brain):     {round(t3 - t2, 2)}s")
    
    # 4. SPEAK TIME
    audio_url = generate_speech(ai_reply)
    t4 = time.time()
    print(f"👄 Murf (Mouth):     {round(t4 - t3, 2)}s")
    
    # TOTAL
    total_time = round(t4 - start_total, 2)
    print(f"🏁 TOTAL BACKEND:    {total_time}s")
    print("------------------------------------------------")
    
    if audio_url:
        return jsonify({
            "message": "Success",
            "text": ai_reply,
            "audio_url": audio_url
        })
    else:
        return jsonify({"error": "Failed to generate speech"}), 500

if __name__ == '__main__':
    print("🔥 SERENITY DEBUGGER ONLINE")
    app.run(debug=True, port=5000)
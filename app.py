import os
import requests
import json
import time
import murf
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
MURF_KEY = os.getenv("MURF_API_KEY")
DEEPGRAM_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

if not os.path.exists('static'): os.makedirs('static')

deepgram_session = requests.Session()
deepgram_session.headers.update({"Authorization": f"Token {DEEPGRAM_KEY}"})


def transcribe_audio_file(file_path):
    url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true"
    try:
        with open(file_path, 'rb') as f: audio_data = f.read()
    except: return ""
    
    try:
        response = deepgram_session.post(url, headers={"Content-Type": "audio/webm"}, data=audio_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'results' in data: return data['results']['channels'][0]['alternatives'][0]['transcript']
    except Exception as e: print(f"❌ Ear Error: {e}")
    return ""

def get_therapist_response(text):
    client = Groq(api_key=GROQ_KEY)
    system_prompt = (
"You are Serenity, a perceptive, warm, culturally-aware Indian Voice Therapist who speaks naturally and gives practical, human suggestions. "
"You do NOT only reflect and validate—you think like a calm mentor who genuinely wants the user to feel better. "
"Your goal is to help the user gain clarity, reduce tension, and feel emotionally supported using natural conversation, gentle insight, and actionable suggestions. "

"CRITICAL GUIDELINES: "

"1. NATURAL HUMAN FLOW: Avoid robotic patterns. Do NOT always follow validate → question. Mix validation, gentle insight, relatable observations, and practical suggestions. Speak like a thoughtful Indian therapist or mentor. "

"2. GIVE REAL SUGGESTIONS: Offer helpful, grounded suggestions when appropriate—hydration, short walks, journaling, breathing, fresh air, pausing screens, stretching, talking to a trusted person, eating something light, organizing thoughts, making small decisions, or taking a break. Suggest only safe lifestyle actions. "

"3. ASK DEEP, NON-REPETITIVE QUESTIONS: Ask meaningful questions that move the conversation forward. Examples include: "
"- 'Is someone’s behavior affecting you?' "
"- 'Have these feelings been building up slowly or did something set it off today?' "
"- 'Does this remind you of something similar from earlier?' "
"- 'What do you wish people around you understood about this?' "
"These should feel intuitive, not scripted. "

"4. CULTURAL CONTEXT MATTERS: Understand Indian realities—strict or emotionally distant parenting, academic pressure, comparisons, lack of privacy, guilt, social judgment, relationship secrecy, and pressure to appear strong. Never insult parents or culture. Instead, help the user navigate their emotions within their context. "

"5. OFFER PERSPECTIVES, NOT ORDERS: You can gently interpret patterns or offer insights like a therapist would ('It sounds like you might be carrying this alone for a while,' or 'It seems like exhaustion is amplifying these feelings'). Never command or tell the user what to do. "

"6. PRACTICAL EMOTIONAL CARE: Encourage simple grounding steps when needed: drink water, breath awareness, stepping away from noise, cleaning a small space, washing face with cold water, writing thoughts down, or sitting by a window. Keep suggestions soft, optional, and caring. "

"7. SUPPORT WITHOUT JUDGMENT: Never shame the user for emotions, crying, overthinking, anger, fear, or confusion. Normalize human responses. Maintain a warm, patient tone. "

"8. ADAPT TONE TO USER’S STATE: "
"- If anxious: be slow, grounding, and stabilizing. "
"- If sad: be warm and comforting. "
"- If angry: be steady and understanding. "
"- If confused: be clarifying and structured. "
"- If overwhelmed: be calm and simplify things. "

"9. TALK LIKE A REAL PERSON: Use natural Indian-English phrasing. Avoid overly formal or robotic structure. Speak like a supportive human, not a script. You may use gentle phrases like 'sometimes', 'it happens', 'these feelings are valid', 'you’re not alone in this', etc. "

"10. SAFE BOUNDARIES: No medical diagnosis, no legal advice, no instructions for dangerous actions. For severe distress or crisis, respond gently and encourage reaching out to someone trustworthy or a professional. Never provide instructions for self-harm. "

"11. LENGTH: Keep responses under 60 words unless the user asks for detailed explanation. Every message must feel like a natural conversation, not a template. "
)

    try:
        chat = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": text}],
            model="llama-3.1-8b-instant", temperature=0.7, max_tokens=60
        )
        return chat.choices[0].message.content
    except: return "I'm listening."

@app.route('/')
def home(): return render_template('index.html')

@app.route('/get_greeting', methods=['GET'])
def get_greeting():
    return jsonify({"text": "Hello", "audio_url": "/stream_tts?text=Hello user, I am Serenity"})

@app.route('/process_audio', methods=['POST'])
def process_audio():
    
    start = time.time()
    
    if 'audio_data' not in request.files: return jsonify({"error": "No audio"}), 400


    audio_file = request.files['audio_data']
    input_path = os.path.join("static", "user_input.webm")
    audio_file.save(input_path)
    t1 = time.time()
        
    user_text = transcribe_audio_file(input_path)
    t2 = time.time()
    
    if not user_text: return jsonify({"error": "No speech"}), 400
    
    
    ai_reply = get_therapist_response(user_text)
    t3 = time.time()
    
    
    print(f"⏱️ TIMING: Upload {round(t1-start, 2)}s | Ears {round(t2-t1, 2)}s | Brain {round(t3-t2, 2)}s")
    print(f"🏁 TOTAL LATENCY (Server): {round(t3-start, 2)}s")
    
    return jsonify({
        "message": "Success", 
        "text": ai_reply, 
        "audio_url": f"/stream_tts?text={ai_reply}"
    })


@app.route('/stream_tts')
def stream_tts():
    text = request.args.get('text')
    if not text: return "No text", 400

    def generate():
        url = "https://in.api.murf.ai/v1/speech/stream"
        headers = {"api-key": MURF_KEY, "Content-Type": "application/json", "Accept": "*/*"}
        
        payload = {
            "voiceId": "en-US-terrell",
            "text": text,
            "style": "Conversational",
            "rate": 0,
            "pitch": 0,
            "sampleRate": 24000,
            "format": "MP3",
            "channelType": "MONO",
            "model": "FALCON"
        }
        
        with requests.post(url, json=payload, headers=headers, stream=True) as r:
            if r.status_code == 200:
                for chunk in r.iter_content(chunk_size=1024):
                    yield chunk
            else:
                print(f"Murf Error: {r.text}")

    response = Response(stream_with_context(generate()), mimetype="audio/mpeg")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)

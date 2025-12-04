# 🧘‍♀️ Serenity AI - Therapeutic Voice Consultant

**Serenity** is a real-time, empathetic AI voice consultant designed to provide immediate emotional support and actionable clarity. Unlike standard chatbots, Serenity uses **Voice Activity Detection (VAD)** for a completely hands-free, fluid conversational experience.

## 🚀 Key Features
* **Hands-Free Interaction:** Speaks and listens automatically without pushing buttons.
* **Living Core UI:** A dynamic, holographic visual interface that reacts organically to user voice volume and AI processing states.
* **Emotional Intelligence:** Powered by **Llama 3.1 8B** (via Groq) to provide validation and actionable advice.
* **Hyper-Realistic Voice:** Uses **Murf Falcon** (Streaming Mode) for sub-second, human-like speech generation.

## 🛠️ Tech Stack
* **Frontend:** HTML5, CSS3 (Advanced Animations), JavaScript (MediaRecorder API)
* **Backend:** Python (Flask) with optimized Streaming Pipelines
* **Speech-to-Text (Ears):** Deepgram Nova-2 (via REST API)
* **Intelligence (Brain):** Groq (Llama 3.1)
* **Text-to-Speech (Mouth):** **Murf Falcon API** (Streaming Endpoint)

## ⚡ Setup Instructions

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/Serenity-Voice-Therapist.git](https://github.com/YOUR_USERNAME/Serenity-Voice-Therapist.git)
    cd Serenity-Voice-Therapist
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Keys**
    Create a `.env` file in the root directory and add your keys:
    ```env
    MURF_API_KEY=your_murf_key
    DEEPGRAM_API_KEY=your_deepgram_key
    GROQ_API_KEY=your_groq_key
    ```

4.  **Run the Server**
    ```bash
    python app.py
    ```
    Open your browser to `http://localhost:5000`

## 🎥 Demo
[Insert link to your demo video here or upload 'demo.mp4' to this repository]

---
*Built for the Techfest IIT Bombay x Murf.ai Hackathon 2025.*

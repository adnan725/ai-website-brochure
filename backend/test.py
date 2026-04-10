from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from werkzeug.utils import secure_filename
from openai import OpenAI
from huggingface_hub import login
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"
import shutil
print("FFMPEG PATH:", shutil.which("ffmpeg"))
from transformers import pipeline
import torch

app = Flask(__name__)
CORS(
    app,
    resources={r"/api/*": {"origins": [
        "https://brochureai.netlify.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000", 
        "http://127.0.0.1:5173"
    ]}},
    supports_credentials=True
)

#### AI setup ####

MODEL = "gpt-4o-mini"
token=os.getenv("HF_TOKEN")
api_openai_key = os.getenv("OPENAI_API_KEY")
if api_openai_key:
    openai = OpenAI(api_key=api_openai_key)
if token:
    login(token, add_to_git_credential=True)

transcribe_audio = None

def get_transcriber():
    global transcribe_audio
    if transcribe_audio is None:
        transcribe_audio = pipeline(
            "automatic-speech-recognition",
            model='openai/whisper-base.en',
            device=-1,
            return_timestamps=True 
        )
    return transcribe_audio

system_message = """
You produce minutes of meetings from transcripts, with summary, key discussion points,
takeaways and action items with owners, in markdown format without code blocks.
"""

app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

def get_meeting_minutes(file):
    print('Transcribing audio...', file)
    transcription = get_transcriber()(file)
    transcription_text = transcription["text"]
    print('transcription: ', transcription)

    user_prompt = f"""
Below is an extract transcript of a Denver council meeting.
Please write minutes in markdown without code blocks, including:
- a summary with attendees, location and date
- discussion points
- takeaways
- action items with owners

Transcription: {transcription_text}
"""
    
    messages=[
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt}
    ]

    result = openai.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=2048,
        temperature=0.7,
    )

    return result.choices[0].message.content

@app.route("/", methods=["GET"])
def home():
    return "Server is running ✅"

@app.route("/test-openai")
def test_openai():
    res = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello"}],
    )
    return res.choices[0].message.content

@app.route("/api/meeting-minutes", methods=["POST"])
def upload_audio():
    try:
        # Check if file is present
        if "audio" not in request.files:
            return jsonify({"error": "No file part in request"}), 400

        file = request.files["audio"]

        # Check if file is selected
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Optional: validate file type
        if not file.filename.endswith(".mp3"):
            return jsonify({"error": "Only .mp3 files are allowed"}), 400

        filename = secure_filename(file.filename)

        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)


        transcription = get_meeting_minutes(file_path)
        print('transcription: ', transcription)



        return jsonify({
            "message": "File transcribed successfully",
            "minutes": transcription,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Starting test server...")
    app.run(host="127.0.0.1", port=5000, debug=True)
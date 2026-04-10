import os
from flask import Flask, json, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from bs4 import BeautifulSoup
import requests

# ─── App setup ───────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = "http://localhost:11434/v1"
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

def fetch_website_contents(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string if soup.title else "No title found"
    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""
    return (title + "\n\n" + text)[:2_000]

def fetch_website_links(url):
    """
    Return the links on the webiste at the given url
    I realize this is inefficient as we're parsing twice! This is to keep the code in the lab simple.
    Feel free to use a class and optimize it!
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = [link.get("href") for link in soup.find_all("a")]
    return [link for link in links if link]

# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/api/summarize", methods=["POST", "OPTIONS"])
def summarize():
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200

    data = request.get_json()

    url = data.get("url", "")
    question = data.get("question", "")

    
    summary = fetch_website_contents(url)
    #openai = OpenAI()
    ollama = OpenAI(base_url=OLLAMA_BASE_URL, api_key='ollama')

    #lets use gemeni open source modal instead of openai

    system_prompt = f"""
    You are a professional web page summarizer and translator.
    Use ONLY the provided website content to answer.
    Website Content: {summary}
    Always answer based on this content and translate the response into the language requested by the user.
    """

    user_prompt = f"""
    Summarize the content of the web page in relation to the user's query.
    User Question: {question}
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    ## openai with openai modal
    #response = ollama.chat.completions.create(model="gpt-5-nano", messages=messages)

    ## deepseek llm through ollama with openai python library
    response = ollama.chat.completions.create(model="deepseek-r1:1.5b", messages=messages)
    result = response.choices[0].message.content
     

    return jsonify({"answer": result})

@app.route("/api/ask", methods=["POST", "OPTIONS"])
def ask():

    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200

    data = request.get_json()
    question = data.get("question", "")
    print("Received question:", question)

    openai = OpenAI()
    response = openai.chat.completions.create(model="gpt-5-nano", messages=[
        {"role": "user", "content": question}
])
    result = response.choices[0].message.content
    print("Generated answer:", result)
    return jsonify({"answer": result})

@app.route("/api/create-brochure", methods=["POST"])
def create_brochure():

    try:
        client = OpenAI()

        data = request.get_json()
        url = data.get("url", "").strip()

        if not url:
            return jsonify({"error": "URL is required"}), 400

        def fetch_website_contents(url):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")

                if soup.body:
                    for tag in soup(["script", "style", "img", "input"]):
                        tag.decompose()
                    text = soup.body.get_text(separator="\n", strip=True)
                else:
                    text = ""

                title = soup.title.string if soup.title else ""
                return (title + "\n\n" + text)[:2000]

            except Exception as e:
                print("❌ Fetch error:", e)
                return "Could not fetch content"

        content = fetch_website_contents(url)

        messages = [
            {
                "role": "system",
                "content": """
You are an expert copywriter.
Create a professional company brochure in clean markdown.
Include:
- Company overview
- Services/products
- Value proposition
- Optional careers or culture
Keep it structured with headings.
"""
            },
            {
                "role": "user",
                "content": f"Website content:\n{content}"
            }
        ]

        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
            )
            brochure = response.choices[0].message.content

        except Exception as e:
            print("❌ OpenAI error:", e)
            return jsonify({"error": "AI generation failed"}), 500

        return jsonify({"brochure": brochure})

    except Exception as e:
        print("❌ Unexpected error:", e)
        return jsonify({"error": str(e)}), 500
    
# ─── Entry point ─────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def home():
    return "Flask is running ✅"

@app.route("/api/key", methods=["GET"])
def get_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    return jsonify({"api_key": api_key})

from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Folder to store uploaded files
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


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

        # Save file (optional but useful)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        return jsonify({
            "message": "File received successfully",
            "filename": file.filename,
            "path": file_path
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n WARNING: OPENAI_API_KEY environment variable is not set.\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
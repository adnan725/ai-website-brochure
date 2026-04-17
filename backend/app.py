import os
import redis
from dotenv import load_dotenv
import requests
from flask import Flask
from flask_cors import CORS
from bs4 import BeautifulSoup
from routes.chat import chat_blueprint
from routes.upload_files import upload_files_blueprint
from routes.create_brocure import create_brocure_blueprint

# ─── App setup ───────────────────────────────────────────────────────────────
load_dotenv()
OLLAMA_BASE_URL = "http://localhost:11434/v1"
ENCODING_MODEL = "gpt-4.1-nano"
db_name = "vector_db"
UPLOAD_FOLDER = "./uploads"
token=os.getenv("HF_TOKEN")

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


@app.route("/", methods=["GET"])
def home():
    return "Flask is running ✅"


##### Blueprints #####
app.register_blueprint(chat_blueprint)
app.register_blueprint(upload_files_blueprint)
app.register_blueprint(create_brocure_blueprint)


r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

print(r.ping())

if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n WARNING: OPENAI_API_KEY environment variable is not set.\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
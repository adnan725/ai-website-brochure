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

    # For simplicity, we'll use the same LLM for both summarization and answering
    # In a real-world scenario, you might want to use different prompts or models
    openai = OpenAI()
    response = openai.chat.completions.create(model="gpt-5-nano", messages=[
        {"role": "user", "content": question}
])
    result = response.choices[0].message.content
    print("Generated answer:", result)
    return jsonify({"answer": result})


@app.route("/api/create-brochure", methods=["POST", "OPTIONS"])
def create_brochure():
    openai = OpenAI()
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200
    
    data = request.get_json()
    url = data.get("url", "")

    link_system_prompt = f"""
You are provided with a list of links found on a webpage.
You are able to decide which of the links would be most relevant to include in a brochure about the company,
such as links to an About page, or a Company page, or Careers/Jobs pages.
You should respond in JSON as in this example:

{{
    "links": [
        {{"type": "about page", "url": "https://full.url/goes/here/about"}},
        {{"type": "careers page", "url": "https://another.full.url/careers"}}
    ]
}}
"""

    def get_links_user_prompt(url):
        user_prompt = f"""
        Here is the list of links on the website {url} -
        Please decide which of these are relevant web links for a brochure about the company, 
        respond with the full https URL in JSON format.
        Do not include Terms of Service, Privacy, email links.

        Links (some might be relative links):

        """
        links = fetch_website_links(url)
        user_prompt += "\n".join(links)
        return user_prompt

    def select_relevant_links(url):
        response = openai.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": link_system_prompt},
                {"role": "user", "content": get_links_user_prompt(url)}
            ],
        response_format={"type": "json_object"}
    )
        result = response.choices[0].message.content
        links = json.loads(result)
        return links
    
    def fetch_page_and_all_relevant_links(url):
        contents = fetch_website_contents(url)
        relevant_links = select_relevant_links(url)
        result = f"## Landing Page:\n\n{contents}\n## Relevant Links:\n"
        for link in relevant_links['links']:
            result += f"\n\n### Link: {link['type']}\n"
            result += fetch_website_contents(link["url"])
        return result
    
    brochure_system_prompt = """
You are an assistant that analyzes the contents of several relevant pages from a company website
and creates a short brochure about the company for prospective customers, investors and recruits.
Respond in markdown without code blocks.
Include details of company culture, customers and careers/jobs if you have the information.
"""

    def get_brochure_user_prompt(company_name, url):
        user_prompt = f"""
You are looking at a company called: {company_name}
Here are the contents of its landing page and other relevant pages;
use this information to build a short brochure of the company in markdown without code blocks.\n\n
"""
        user_prompt += fetch_page_and_all_relevant_links(url)
        user_prompt = user_prompt[:5_000] # Truncate if more than 5,000 characters
        return user_prompt
    
    def create_brochure(company_name, url):
        response = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": brochure_system_prompt},
                {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
            ],
        )
        result = response.choices[0].message.content
        return result

    return jsonify({"brochure": create_brochure("HuggingFace", url)})

# ─── Entry point ─────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def home():
    return "Flask is running ✅"

@app.route("/api/key", methods=["GET"])
def get_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    return jsonify({"api_key": api_key})

if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n WARNING: OPENAI_API_KEY environment variable is not set.\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
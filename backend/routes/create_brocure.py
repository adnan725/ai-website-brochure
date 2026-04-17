from flask import app, request, jsonify, Blueprint
from bs4 import BeautifulSoup
import requests
from openai import OpenAI

create_brocure_blueprint = Blueprint("create_brocure", __name__)

@create_brocure_blueprint.route("/api/create-brochure", methods=["POST"])
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
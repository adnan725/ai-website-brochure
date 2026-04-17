import os
import redis
from langchain_openai import ChatOpenAI


openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.2, api_key=openai_api_key)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def save_summary_to_redis(session_id, summary):
    redis_client.set(f"chat:{session_id}:summary", summary)

def get_summary_from_redis(session_id):
    summary = redis_client.get(f"chat:{session_id}:summary") or ""
    return summary.decode("utf-8") if summary else ""

def update_summary(session_id, messages, old_summary):
    text = "\n".join([m["content"] for m in messages])

    prompt = f"""
Previous summary:
{old_summary}

New conversation:
{text}

Update the summary.
"""
    summary = llm.invoke(prompt).content
    
    save_summary_to_redis(session_id, summary)

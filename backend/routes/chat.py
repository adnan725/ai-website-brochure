from flask import request, jsonify, Blueprint
from utils.helpers import generate_answer
from memory.short_term_memory import save_recent_to_redis, get_recent_from_redis
from memory.summary_memory import update_summary, get_summary_from_redis
from memory.vector_memory import save_conversation_to_memory_vector
from memory.context_builder import build_context

chat_blueprint = Blueprint("chat", __name__)

@chat_blueprint.route("/api/chat", methods=["POST", "OPTIONS"])
def ask():

    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200

    data = request.get_json()
    question = data.get("message", "")
    session_id = data.get("sessionId", None)

    if not session_id:
        return jsonify({"error": "sessionId is required"}), 400

    save_recent_to_redis(session_id, "user", question)

    memory_context = build_context(session_id, question)

    answer = generate_answer(question, memory_context)  

    save_recent_to_redis(session_id, "assistant", answer)
    save_conversation_to_memory_vector(session_id, question, answer)

    old_summary = get_summary_from_redis(session_id)
    recent_messages = get_recent_from_redis(session_id)
    update_summary(session_id, recent_messages, old_summary)


    return jsonify({"answer": answer})
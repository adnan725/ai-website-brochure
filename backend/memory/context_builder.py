from memory.short_term_memory import get_recent_from_redis
from memory.summary_memory import get_summary_from_redis
from memory.vector_memory import get_conversation_from_memory_vector

def build_context(session_id, question):
    summary = get_summary_from_redis(session_id)
    recent = get_recent_from_redis(session_id)
    relevant = get_conversation_from_memory_vector(session_id, question)

    recent_text = "\n".join(
        [f"{m['role']}: {m['content']}" for m in recent]
    )

    relevant_text = "\n".join(relevant)

    memory_context = f"""
    You are a knowledgeable, friendly assistant at a InfoRAG company. You answer should not be 
    more than 30 words and should be precise and accurate. DO not hellucinate. If you do not find any 
    relavant embeddings, simply ask tell politely i do not know please ask me about InfoAG.
    You will get the summary of the conversation, recent conversation history, 
    and relevant past memory to answer the user's question.
    
    Conversation Summary:
    {summary}
    
    Recent Conversation:
    {recent_text}
    
    Relevant Past Memory:
    {relevant_text}
    
    User Question:
    {question}
    """

    return memory_context
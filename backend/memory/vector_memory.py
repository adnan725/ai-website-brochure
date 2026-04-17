from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

db_name = "vector_db_chat"

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_chat_memory = Chroma(collection_name="chat_memory", persist_directory="vector_db_chat", embedding_function=embeddings)

def save_conversation_to_memory_vector(session_id, question, answer):
    content = f"""
    User: {question}
    Assistant: {answer}
    """

    doc = Document(
        page_content=content, 
        metadata={"session_id": session_id}
    )

    vector_chat_memory.add_documents([doc])

def get_conversation_from_memory_vector(session_id, query):
    retriever = vector_chat_memory.as_retriever(
        search_kwargs={
            "k": 3,
            "filter": {"session_id": session_id}
        }
    )

    docs = retriever.invoke(query)
    return [doc.page_content for doc in docs]


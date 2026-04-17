import os
from dotenv import load_dotenv
from flask import Flask, json, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from bs4 import BeautifulSoup
import requests
from huggingface_hub import login
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
#from langchain_core import Document
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader, CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken
import glob
from langchain_core.messages import SystemMessage, HumanMessage


load_dotenv()
ENCODING_MODEL = "gpt-4.1-nano"
db_name = "vector_db"
UPLOAD_FOLDER = "./uploads"
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0.2, api_key=api_key)

def get_retriever():
    vectorstore = Chroma(
        collection_name="documents",
        persist_directory=db_name,
        embedding_function=embeddings
    )
    print("TOTAL DOCS:", vectorstore._collection.count())
    return vectorstore.as_retriever(search_kwargs={"k": 3})

def tiktoken_len(text):
    tokenizer = tiktoken.encoding_for_model(ENCODING_MODEL)
    return len(tokenizer.encode(text))

def generate_answer(question, memory_context):

    SYSTEM_PROMPT_TEMPLATE = """
Here is the memory_context:
{memory_context}

here is the documents Context:
{context}
"""
    retriever = get_retriever()
    docs = retriever.invoke(question)
    doc_context = "\n\n".join([doc.page_content for doc in docs])

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=doc_context, memory_context=memory_context)
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=question)])
    return response.content


def process_uploaded_files(files):

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(collection_name="documents", persist_directory=db_name, embedding_function=embeddings)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100, length_function=tiktoken_len)

    for file in files:
        print(f"Processing file: {file.filename}")

        file_path = f"{UPLOAD_FOLDER}/{file.filename}"
        file.save(file_path)

        if file.filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file.filename.endswith(".csv"):
            loader = CSVLoader(file_path)
        else:
            loader = TextLoader(file_path, autodetect_encoding=True)

        documents = loader.load()

        for doc in documents:
            doc.metadata["source"] = file.filename

        chunks = splitter.split_documents(documents)

        # 🔥 THIS LINE CREATES EMBEDDINGS
        vectorstore.add_documents(chunks)

    del vectorstore
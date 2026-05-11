from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import sys
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import CSVLoader,PyPDFLoader
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from langchain_core.messages import SystemMessage
from transformers import AutoTokenizer,AutoModelForSequenceClassification
from huggingface_hub import login
from sentence_transformers import CrossEncoder
from langchain_community.llms import OpenAI
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor
from dotenv import load_dotenv
import os
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
from langchain_core.documents import Document
from torch import embedding

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR.parent / "src"))

#
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
template = ChatPromptTemplate.from_messages([
    ("system", "You are a precise assistant. Answer ONLY using the provided context. And make sure that te output looks good and readable."),
    ("human",
     "Context:\n{context}\n\n"
     "Question:\n{question}")
])


def load_vector_store():
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    return Chroma(
        persist_directory=str(BASE_DIR / "chroma_db"),
        embedding_function=embedding_model,
    )
load_dotenv('secret.env')
key = os.getenv("Open_Ai_Key")
model = ChatOpenAI(
    model_name="openai/gpt-oss-120b:free",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=key,
)
def query_rewrite(query):
  template = PromptTemplate(
      input_variables=["query"],
      template=(
          "You are an expert in information retrieval.\n"
          "Rewrite the following user query to be more specific, detailed, "
          "and aligned with terminology likely used in technical and regulatory documents.\n"
          "Do NOT answer the query.\n"
          "Return ONLY the rewritten query.\n\n"
          "Original query: {query}"
          )
  )
  chain = template|model
  return chain.invoke({"query":query})
def Rerank_docs(query, vector_store):
    docs = retrive_docs(vector_store, query)
    Reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L12-v2")
    pairs = [(query, d.page_content) for d in docs]
    scores = Reranker.predict(pairs)
    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in ranked]
def retrive_docs(vector_store, query):
    Retrival = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
    )
    docs = Retrival.invoke(query)
    return docs
import re

def clean_response(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)   
    text = re.sub(r'\n{3,}', '\n\n', text)           
    text = text.strip()
    return text

def Build_response(query, vector_store):
    top_docs = Rerank_docs(query, vector_store)
    print(f"[DEBUG] Retrieved {len(top_docs)} docs")
    context = "\n\n".join(d.page_content for d in top_docs)
    rag_chain = template | model
    response = rag_chain.invoke({"context": context, "question": query})
    return clean_response(response.content)
vector_store = load_vector_store()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.get("/")
def root():
    return FileResponse(str(BASE_DIR / "static" / "api.html"))

class Question(BaseModel):
    question: str

@app.post("/ask")
async def ask(q: Question):
    try:
        rewritten = query_rewrite(q.question).content 
        answer = Build_response(rewritten, vector_store)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"Error: {str(e)}"}
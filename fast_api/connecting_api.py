from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import sys

# Absolute path to src
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR.parent / "src"))

# Import RAG functions
from main import Build_response, query_rewrite

# Load vector store from disk (no re-scraping/re-embedding)
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def load_vector_store():
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    return Chroma(
        persist_directory=str(BASE_DIR.parent / "chroma_db"),
        embedding_function=embedding_model,
    )

vector_store = load_vector_store()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Absolute paths for static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.get("/")
def root():
    return FileResponse(str(BASE_DIR / "static" / "api.html"))

class Question(BaseModel):
    question: str

@app.post("/ask")
async def ask(q: Question):
    try:
        rewritten = query_rewrite(q.question).content  # main.py returns AIMessage
        answer = Build_response(rewritten, vector_store)
        return {"answer": answer}
    except Exception as e:
        return {"answer": f"Error: {str(e)}"}
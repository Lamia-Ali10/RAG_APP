# embedding_index.py
from torch import embedding

from preprocess import preprocess_all, chunk_all
from data_loader import load_all_documents
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

def build_emb_model(embedding_type: str = "paragraph"):
    model = "sentence-transformers/all-MiniLM-L6-v2"
    if embedding_type=="paragraph":
        encode_kwargs = {"normalize_embeddings": True}
        model_kwargs = {"device": "cpu"}
        embedding_model = HuggingFaceEmbeddings(
            model_name=model,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
        )
    elif embedding_type=="query":
        encode_kwargs = {"normalize_embeddings": True}
        model_kwargs = {"device": "cpu"}
        embedding_model = HuggingFaceEmbeddings(
            model_name=model,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
            query_instruction="Represent this query for retrieving relevant documents: ",
        )
    return embedding_model


def build_vector_db():
    raw_docs = load_all_documents()
    clean_docs = preprocess_all(raw_docs)
    all_chunks = chunk_all(clean_docs)
    docs = [
        Document(
            page_content=chunk["content"],
            metadata={
                "disease": chunk["disease"],
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"]
            }
        )
        for chunk in all_chunks
    ]
    embedding_model = build_emb_model(embedding_type="paragraph")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory="./chroma_db"
    )
    return vectorstore

def build_user_query(query:str):
    embedding_model = build_emb_model(embedding_type="query")
    query_vector = embedding_model.embed_query(query)
    return query_vector
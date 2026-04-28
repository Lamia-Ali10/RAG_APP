# embedding_index.py
from preprocess import preprocess_all, chunk_all
from data_loader import load_all_documents
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


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

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory="./chroma_db"
    )

    return vectorstore


if __name__ == "__main__":
    build_vector_db()
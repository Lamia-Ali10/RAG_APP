# 🏥 Medical QA — RAG System

A containerised **Retrieval-Augmented Generation (RAG)** system that answers health questions using verified medical documents. Built with FastAPI, ChromaDB, HuggingFace embeddings, and a multi-model LLM factory — deployed via Docker Compose.

---

## ✨ Features

- 🔍 **Semantic retrieval** — vector similarity search over indexed medical documents (ChromaDB)
- ✏️ **Query rewriting** — rewrites user questions into domain-aligned terminology before retrieval
- 📊 **Cross-encoder re-ranking** — re-scores retrieved chunks for higher precision
- 🤖 **LLM Factory Pattern** — switch between 4 language models at runtime via a single API parameter
- 🚫 **Hallucination guard** — LLM is strictly constrained to answer only from retrieved context
- 🐳 **Fully containerised** — runs with a single `docker-compose up` command

---

## 🏗️ Architecture

```
User Browser
    │
    ├─── GET /          ──► frontend-1 (Nginx · port 80)
    │                        HTML / CSS / JS
    │
    └─── POST /ask      ──► backend-1 (FastAPI · port 5000)
                              │
                              ├── ① Query rewriter (LLM)
                              ├── ② ChromaDB vector retrieval (k=3)
                              ├── ③ CrossEncoder re-ranking
                              ├── ④ LLM answer generation
                              │
                              ├── ChromaDB (persisted volume)
                              └── OpenRouter API (4 models)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML / CSS / JS · Nginx |
| Backend | FastAPI · Uvicorn · Python 3.11 |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector Store | ChromaDB (persisted) |
| Re-ranker | `cross-encoder/ms-marco-MiniLM-L12-v2` |
| LLM | OpenRouter API (GPT, Owl, InclusionAI, Qwen) |
| Deployment | Docker · Docker Compose |

---

## 📁 Project Structure

```
NLP Project/
├── connecting_api.py       # FastAPI backend — full RAG logic
├── Dockerfile              # Backend image
├── req.txt                 # Python dependencies
├── docker-compose.yml      # Multi-service orchestration
├── secret.env              # API keys (⚠️ not committed)
├── chroma_db/              # Persisted vector store
├── Data/                   # Raw medical source documents
└── static/
    ├── api.html            # Chat interface
    ├── api.css             # Styles
    ├── api.js              # Frontend logic
    └── Dockerfile          # Frontend Nginx image
```

---

## 🚀 Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 4.x
- Docker Compose v2

### 1. Clone the repository

```bash
git clone https://github.com/your-username/nlp-medical-qa.git
cd nlp-medical-qa
```

### 2. Set up your API key

Create a `secret.env` file in the project root:

```env
Open_Ai_Key=your_openrouter_api_key_here
```

> Get a free API key at [openrouter.ai](https://openrouter.ai)

### 3. Build and run

```bash
docker-compose up --build -d
```

### 4. Wait for the backend to load

The embedding model and ChromaDB initialise on cold start. Monitor progress:

```bash
docker logs nlpproject-backend-1 --follow
```

Ready when you see:
```
Uvicorn running on http://0.0.0.0:5000
```

### 5. Open the app

Navigate to **http://localhost** in your browser.

---

## 📡 API Reference

### `POST /ask`

Runs the full RAG pipeline and returns a grounded answer.

**Request**
```json
{
  "question": "What are the early symptoms of diabetes?",
  "model": "gpt"
}
```

**Response**
```json
{
  "answer": "Early symptoms of diabetes include increased thirst, frequent urination, blurred vision, and fatigue..."
}
```

**Available models**

| Key | Model |
|---|---|
| `gpt` | openai/gpt-oss-120b:free |
| `owl` | openrouter/owl-alpha |
| `inclusionai` | inclusionai/ring-2.6-1t:free |
| `qween` | qwen/qwen3-next-80b-a3b-instruct:free |

> Interactive API docs available at **http://localhost:5000/docs**

---

## 🧠 RAG Pipeline

1. **Query rewriting** — the user's question is rewritten into precise medical terminology by the LLM to improve retrieval accuracy
2. **Vector retrieval** — the rewritten query is embedded with `all-MiniLM-L6-v2` and the top-3 most similar chunks are retrieved from ChromaDB
3. **Re-ranking** — all 3 candidates are jointly scored against the query by a CrossEncoder and sorted by relevance
4. **Answer generation** — top chunks are injected as context into the LLM, which generates an answer strictly grounded in the retrieved content

---

## 🏭 LLM Factory Pattern (Bonus)

The system implements the **Factory Design Pattern** for model selection. Pass any supported model key in the API request body — no server restart or config change required.

```python
class LLMFactory:
    def __init__(self):
        self.models = {
            "gpt":         "openai/gpt-oss-120b:free",
            "owl":         "openrouter/owl-alpha",
            "inclusionai": "inclusionai/ring-2.6-1t:free",
            "qween":       "qwen/qwen3-next-80b-a3b-instruct:free",
        }

    def get_model(self, model_name):
        return ChatOpenAI(
            model_name=self.models[model_name],
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=self.key,
        )
```

---

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Rebuild a single service (no full reinstall)
docker-compose up --build -d backend

# Stop all services
docker-compose down

# View backend logs
docker logs nlpproject-backend-1 --tail 50

# Free up disk space
docker system prune -a
```

---

## ⚠️ Important Notes

- `secret.env` is listed in `.gitignore` and must **never** be committed
- The backend uses ~500MB RAM to load the embedding model on startup
- Cold start takes 1–2 minutes — wait for the Uvicorn log before testing

---

## 👥 Team

| Name | ID |
|---|---|
| عمر رامي السيد محمد — Omar Rami El-Sayed | 2023170390 |
| جانا سمير مصطفى محمد — Jana Samir Mustafa | 2023170159 |
| لمياء مصطفى كمال على — Lamia Mustafa Kamal | 2023170456 |
| ندى عمرو عبدالحميد احمد — Nada Amr Abdel-Hamid | 2023170664 |
| مي مصطفي احمد يوسف — Mai Mustafa Ahmed | 2023170651 |
| عبدالله احمد محمد وجيه — Abdullah Ahmed Mohamed | 2023170354 |

---

## 📄 License

This project was built for academic purposes as part of an NLP course final project.

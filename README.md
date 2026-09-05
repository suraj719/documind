# 🧠 DocuMind: Enterprise Autonomous AI Document Intelligence & Knowledge Copilot

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.5.4-FF6F00?style=flat)](https://python.langchain.com/docs/langgraph/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16_pgvector-4169E1?style=flat&logo=postgresql)](https://github.com/pgvector/pgvector)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=flat&logo=streamlit)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**DocuMind** is an enterprise-grade autonomous AI document intelligence and retrieval-augmented generation (RAG) platform. Powered by **FastAPI**, **LangGraph ReAct State Graphs**, **PostgreSQL + pgvector**, and **Streamlit**, DocuMind turns enterprise document repositories into real-time interactive intelligence.

[🌐 Live Demo](https://documind7.streamlit.app)

---

## 🌟 Key Capabilities

- 🤖 **Autonomous ReAct Agent Engine**: Dynamic decision matrix orchestrating semantic document retrieval and live web search via Tavily.
- ⚡ **End-to-End JSON Event Streaming**: Low-latency token-by-token streaming back to the client interface with intermediate tool call visualization.
- 🔒 **Multi-Tenant JWT Security & Isolation**: Granular user isolation across document vector stores, checkpointer memory states, and conversation threads.
- 📄 **Multi-Format Document Parsing**: High-speed ingestion for PDF, DOCX, and TXT files with recursive token chunking and metadata tracking.
- 🧠 **Persistent State Checkpointing**: Asynchronous Postgres state checkpointer (`langgraph-checkpoint-postgres`) preserving full chat history across sessions.
- 🎨 **Modern Dark Glassmorphism UI**: Bespoke Streamlit frontend featuring real-time stream rendering, expandable tool execution traces, and document management.

---

## 🏗️ System Architecture

```mermaid
graph TD
    Client[🎨 Streamlit Modern UI] <-->|HTTP / REST + SSE Stream| API[⚡ FastAPI Engine]
    API <-->|JWT Auth & RBAC| Security[🔒 Auth Middleware]
    API <-->|State & Checkpoints| Postgres[🐘 Postgres Checkpointer]
    API <-->|Embeddings & Similarity| Vector[⚡ PGVector Storage]

    subgraph Agent Loop [LangGraph ReAct Orchestrator]
        API --> Graph[Compiled State Graph]
        Graph --> Model[LLM / GPT-4o]
        Model -->|Need Doc Context| Tool1[retrieve_user_documents]
        Model -->|Need Web Data| Tool2[tavily_search]
        Tool1 --> Vector
    end
```

---

## 🔄 RAG Ingestion & Query Execution Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Streamlit GUI
    participant API as FastAPI Backend
    participant Agent as LangGraph Agent
    participant PGV as PGVector Store

    User->>UI: Upload File (PDF/DOCX/TXT)
    UI->>API: POST /api/v1/documents/upload/{thread_id}
    API->>API: Recursive Character Text Splitter (1000 tokens)
    API->>PGV: Store Embeddings with JSONB Metadata (thread_id, user_id)
    API-->>UI: Upload & Indexing Confirmed

    User->>UI: Submit Query ("Summarize section 4")
    UI->>API: POST /api/v1/chat/{thread_id} (Streaming)
    API->>Agent: Execute ReAct Graph
    Agent->>PGV: Query Vector Store (Cosine Similarity)
    PGV-->>Agent: Return Context Chunks
    Agent-->>API: Stream JSON Events (llm_chunk, tool_call)
    API-->>UI: Render Stream & Tool Steps in Real-Time
```

---

## 💻 Tech Stack

| Component               | Technology               | Description                                                          |
| :---------------------- | :----------------------- | :------------------------------------------------------------------- |
| **Backend Framework**   | FastAPI (Python 3.12)    | Asynchronous, production-grade microservice architecture             |
| **Agent Engine**        | LangGraph & LangChain    | ReAct state graph compiler with custom tools and guardrails          |
| **Vector Store**        | PostgreSQL 16 + pgvector | HNSW/IVFFlat index vector storage with metadata filtering            |
| **Memory Checkpointer** | AsyncPostgresSaver       | Asynchronous state persistence for multi-thread retention            |
| **Frontend UI**         | Streamlit                | Custom dark glassmorphism styling with real-time SSE stream handling |
| **Security**            | OAuth2 + JWT (HS256)     | Password hashing (Bcrypt), token refresh, per-tenant data scoping    |
| **Containerization**    | Docker & Docker Compose  | Multi-container orchestrated deployment pipeline                     |

---

## 📦 Quick Start (Docker Compose)

### 1. Environment Setup

Copy the environment template and configure your API keys:

```bash
cp env.example .env
```

Key `.env` configuration:

```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
POSTGRES_DATABASE=documind_db
PGVECTOR_COLLECTION_NAME=documind_embeddings
```

### 2. Launch Full Stack

Start the containerized stack using Docker Compose:

```bash
docker compose up --build -d
```

### 3. Verify Endpoints

- **Frontend Workspace**: [http://localhost:8501](http://localhost:8501)

---

## 🧰 Local Manual Development

### Backend Service (FastAPI)

```bash
cd backend
python -m venv .venv
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Workspace (Streamlit)

```bash
cd frontend
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
streamlit run gui/main.py
```

---

## 📡 Streaming JSON Event Protocol

DocuMind uses newline-delimited SSE JSON events to deliver real-time agent feedback:

```json
{"type": "tool_call", "name": "retrieve_user_documents", "args": {"query": "contract termination terms"}}
{"type": "tool_result", "name": "retrieve_user_documents", "content": "[Chunk 1: Document Section 4.2...]"}
{"type": "llm_chunk", "content": "According to the contract, termination requires 30 days notice..."}
```

---

## 🛠️ API Reference Catalog

| Category      | Endpoint                               | Method | Description                               |
| :------------ | :------------------------------------- | :----- | :---------------------------------------- |
| **Auth**      | `/api/v1/auth/signup`                  | `POST` | Register workspace account                |
| **Auth**      | `/api/v1/auth/login`                   | `POST` | Authenticate & obtain JWT tokens          |
| **Threads**   | `/api/v1/threads/`                     | `POST` | Create new conversation thread            |
| **Threads**   | `/api/v1/threads/`                     | `GET`  | List active user threads                  |
| **Documents** | `/api/v1/documents/upload/{thread_id}` | `POST` | Ingest and index PDF/DOCX/TXT file        |
| **Documents** | `/api/v1/documents/stats/{thread_id}`  | `GET`  | Retrieve indexing & document stats        |
| **Chat**      | `/api/v1/chat/{thread_id}`             | `POST` | Stream agent response with memory & tools |

---

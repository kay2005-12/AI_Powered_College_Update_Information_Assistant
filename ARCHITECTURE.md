# 🏛️ Architecture Blueprint: AI-Powered College Information Assistant

An end-to-end automated **Retrieval-Augmented Generation (RAG)** architecture for the **College of Engineering & Management, Kolaghat (CEMK)**. The system monitors institutional notices and events, vectorizes and indexes them into Typesense, serves context-grounded answers via a Telegram bot powered by Groq LLMs, and evaluates performance through LangSmith.

---

## 🗺️ System Architecture Diagram

```mermaid
flowchart TD
    subgraph S1["1. Ingestion & Automation (n8n)"]
        A["Institutional Website (Notices & Events)"] -->|Scrape / Schedule| B["n8n Workflow (College_Information_System.json)"]
        B -->|Parse & Deduplicate| C[("Structured Dataset / CSV")]
    end

    subgraph S2["2. Chunking, Embedding & Storage"]
        C -->|Trigger Indexing| D["n8n Indexing (RAG Indexing_Vectorization.json)"]
        D -->|500 char chunk / 50 overlap| E["Text Chunks"]
        E -->|HF Inference API| F["BAAI/bge-small-en-v1.5 (384-dim)"]
        F -->|Index Vectors & Metadata| G[("Typesense Cloud: cemk_documents")]
    end

    subgraph S3["3. Query & RAG Core"]
        U["Telegram User"] <-->|Chat / Messages| H["Telegram Bot (bot.py)"]
        H -->|generate_answer()| I["Generator (generator.py)"]
        I -->|retrieve()| J["Retriever (retriver.py)"]
        J -->|HF Query Embedding| F
        J -->|Multi-Search Vector Query| G
        G -->|Top-5 Matching Chunks| J
        J -->|Context Chunks| I
        I -->|LangChain Prompt + Context| K["ChatGroq (openai/gpt-oss-120b)"]
        K -->|Grounded Answer| I
        I -->|Response| H
    end

    subgraph S4["4. Quality Assurance & Evaluation"]
        L["Evaluation Dataset (data.py)"] -->|Push QA Pairs| M[("LangSmith Hub")]
        M -->|Evaluate Target| N["Evaluation Harness (evalaution.py)"]
        N -->|Run Pipeline| I
        N -->|LLM-as-a-Judge (Groq)| O["4 Metrics:\n• Correctness\n• Relevance\n• Groundedness\n• Retrieval Relevance"]
    end

    style S1 fill:#f0f7ff,stroke:#2563eb,stroke-width:1px
    style S2 fill:#f0fdf4,stroke:#16a34a,stroke-width:1px
    style S3 fill:#faf5ff,stroke:#9333ea,stroke-width:1px
    style S4 fill:#fff7ed,stroke:#ea580c,stroke-width:1px
```

---

## 🔄 End-to-End Data Flow

```text
[ CEMK Website ]
       │
       ▼ (Periodic Polling via n8n)
[ HTML Extraction & Python Parsing ]
       │
       ▼ (Deduplication)
[ Structured CSV / Data Table ]
       │
       ▼ (Text Formatting & Overlapping Chunking: 500 chars / 50 overlap)
[ Hugging Face Inference API: BAAI/bge-small-en-v1.5 (384-dim) ]
       │
       ▼ (Vector & Metadata Ingestion)
[ Typesense Vector DB: cemk_documents ]
       ▲
       │ Cosine Similarity Search (top_k=5)
       │
[ User Query via Telegram Bot ] ──► [ Query Embedding (HF API) ]
                                          │
                                          ▼
                             [ Top-5 Retrieved Chunks ]
                                          │
                                          ▼
                              [ Context Assembly & Prompt ]
                                          │
                                          ▼
                          [ Groq LLM: openai/gpt-oss-120b ]
                                          │
                                          ▼
                               [ Grounded Response ]
                                          │
                                          ▼
                               [ Sent to Telegram User ]
```

---

## 🧩 Architectural Layers & Components

### 1. Ingestion & Automation Layer (`/n8n` & `/data`)
* **Automation Platform:** `n8n` runs scheduled workflows to periodically poll the CEMK institutional website.
* **Extraction:** Scrapes HTML notices and event announcements, executes Python parsing routines, formats metadata (`title`, `date`, `content`, `type`, `link`), and flags duplicates.
* **Storage:** Extracted notices are saved as structured data (`data/Cemk-Notices.csv`).

### 2. Chunking & Vectorization Layer
* **Text Formatting:** Assembles standard key-value text headers (`Title: ... Date: ... Type: ... Content: ...`).
* **Chunking Strategy:** Overlapping character chunking (**500 characters window, 50 characters overlap**) to maintain semantic continuity across boundaries.
* **Embedding Model:** `BAAI/bge-small-en-v1.5` accessed via Hugging Face Inference API, generating dense **384-dimensional** embeddings.
* **Vector Store:** **Typesense Cloud**
  * **Collection:** `cemk_documents`
  * **Document Schema:** `chunk_id`, `text`, `title`, `date`, `type`, `link`, `embedding (float[384])`.

### 3. Application & Serving Layer (`/RAG_Pipeline`)
* **Retriever (`retriver.py`):**
  * Vectorizes user query using the same `BAAI/bge-small-en-v1.5` endpoint.
  * Performs cosine similarity search via Typesense `/multi_search` with `top_k=5`.
  * Extracts and returns the top 5 matching document objects.
* **Generator (`generator.py`):**
  * Joins retrieved chunks into a sanitized context block separated by `\n\n---\n\n`.
  * Orchestrated via LangChain (`ChatPromptTemplate | ChatGroq | StrOutputParser`).
  * LLM: **Groq** powering `openai/gpt-oss-120b` with `temperature=0` for deterministic outputs.
  * Strict guardrail prompt: Constrains responses strictly to provided context in 2–4 sentences; explicitly outputs fallback `"I could not find this information in the CEMK data."` if unsupported.
* **Bot Interface (`bot.py`):**
  * Telegram bot built with `python-telegram-bot` (`ApplicationBuilder`).
  * Asynchronously captures incoming user messages via long-polling, delegates to `generate_answer()`, and replies back to Telegram.

### 4. Evaluation & Benchmarking Layer
* **Dataset Management (`data.py`):**
  * Constructs and manages `cemk-notices-evaluation` on LangSmith with 15 verified ground-truth test cases.
* **LLM-as-a-Judge (`evalaution.py`):**
  * Uses structured JSON schema outputs (`with_structured_output`) powered by Groq.
  * Measures 4 core RAG dimensions:
    1. **Correctness:** Factual accuracy of student answer against ground truth.
    2. **Relevance:** Whether the answer directly addresses the query.
    3. **Groundedness:** Whether the answer contains only facts present in the retrieved chunks (hallucination detection).
    4. **Retrieval Relevance:** Whether the retrieved chunks contain relevant information for the query.

---

## 🗂️ File & Directory Map

```text
AI_Powered_University_Update_Information_Assistant/
├── .env                                  # API keys (HF, Typesense, Groq, Telegram, LangSmith)
├── README.md                             # Comprehensive technical documentation
├── ARCHITECTURE.md                       # Complete architectural blueprint
├── data/
│   └── Cemk-Notices.csv                  # Scraped university notices dataset
├── n8n/
│   ├── College_Information_System.json   # Ingestion, scraping & deduplication flow
│   └── RAG Indexing_Vectorization.json   # Chunking, HF embedding & Typesense indexing flow
└── RAG_Pipeline/
    ├── bot.py                            # Telegram bot client
    ├── retriver.py                       # Hugging Face + Typesense vector retriever
    ├── generator.py                      # LangChain + Groq context-grounded generator
    ├── data.py                           # LangSmith evaluation dataset creator
    └── evalaution.py                     # 4-metric LLM-as-a-Judge benchmark harness
```

---

## ⚙️ Technology Stack Summary

| Layer | Technology | Details / Model |
| :--- | :--- | :--- |
| **Scraping / Workflow Automation** | n8n | Scheduled triggers, HTML parsing, deduplication |
| **Embeddings** | Hugging Face Inference API | `BAAI/bge-small-en-v1.5` (384-dim) |
| **Vector Database** | Typesense Cloud | Collection: `cemk_documents` |
| **LLM Inference** | Groq Cloud | `openai/gpt-oss-120b` (temp=0) |
| **Orchestration Framework** | LangChain Core | LCEL Chains, ChatPromptTemplate |
| **Chat Interface** | python-telegram-bot | Async polling Telegram bot |
| **Observability & QA** | LangSmith | 4-metric LLM-as-a-Judge evaluation |

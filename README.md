# AI-Powered College Information Assistant

An AI-powered information assistant that automatically monitors institutional updates and provides RAG-based question answering through a Telegram bot.

The system combines **n8n automation, Retrieval-Augmented Generation (RAG), Hugging Face embeddings, Typesense vector search, Groq LLMs, LangSmith evaluation, and Telegram** to provide an automated and context-grounded information service.

---

## 🚀 Features

* 🔄 Automated website monitoring using n8n
* 📢 Automatic notification of new updates
* 📄 Structured extraction of notices and events
* ✂️ Text preprocessing and overlapping chunking
* 🧠 Semantic embeddings using BGE-small-en-v1.5
* 🔎 Vector similarity search using Typesense
* 🤖 Context-grounded answer generation using Groq LLM
* 📱 Telegram-based AI assistant
* 📊 RAG evaluation using LangSmith
* 🔐 Environment-variable based API key management
* 🧩 Modular Python-based RAG pipeline

---

# 🏗️ System Architecture

```text
                    Institutional Website
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
             Notices                 Events
                │                       │
                └───────────┬───────────┘
                            │
                            ▼
                     ┌─────────────┐
                     │     n8n     │
                     │  Monitoring │
                     └──────┬──────┘
                            │
                    Extract / Structure
                            │
                            ▼
                   ┌─────────────────┐
                   │ Structured Data │
                   │   Data Table    │
                   └────────┬────────┘
                            │
                            │
                     RAG Indexing
                            │
                            ▼
                    ┌──────────────┐
                    │ Prepare Text │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Chunking   │
                    │ 500 / 50     │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Hugging Face │
                    │  Embeddings  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Typesense   │
                    │  Vector DB   │
                    └──────┬───────┘
                           │
                           │
                    User Question
                           │
                           ▼
                    ┌──────────────┐
                    │ Telegram Bot │
                    │    Python    │
                    └──────┬───────┘
                           │
                           ▼
                    Query Embedding
                           │
                           ▼
                    Typesense Search
                           │
                           ▼
                      Top 5 Chunks
                           │
                           ▼
                    ┌──────────────┐
                    │   Groq LLM   │
                    │ Answer Gen.  │
                    └──────┬───────┘
                           │
                           ▼
                    Telegram Reply


                    ┌──────────────┐
                    │  LangSmith   │
                    │  Evaluation  │
                    └──────────────┘
```

---

# 🔄 1. Automated Data Ingestion

The system uses **n8n** to periodically monitor an institutional website and collect newly published information.

### Workflow

```text
Schedule Trigger
       │
       ├───────────────┐
       ▼               ▼
    Notices          Events
       │               │
       ▼               ▼
 HTML Extraction   HTML Extraction
       │               │
       ▼               ▼
 Python Parsing    Python Parsing
       │               │
       └───────┬───────┘
               ▼
        Structured Data
               │
               ▼
       Duplicate Detection
               │
               ▼
          Data Table
               │
               └──────► Notification
```

The ingestion pipeline extracts:

* Title
* Date
* Content
* Source URL
* Content type

Duplicate detection prevents the same information from being stored repeatedly.

---

# 🧠 2. RAG Indexing Pipeline

Collected information is transformed into searchable knowledge.

```text
Structured Data
      │
      ▼
Prepare Text
      │
      ▼
Chunking
      │
      ▼
Hugging Face Embeddings
      │
      ▼
Format Embeddings
      │
      ▼
Merge Metadata + Embeddings
      │
      ▼
Typesense
```

---

## 2.1 Text Preparation

The raw fields are converted into structured text:

```text
Title: Example Notice

Date: 2026-09-03

Type: Notice

Content:
Published information...
```

Empty or invalid records are skipped during preprocessing.

---

## 2.2 Chunking

Documents are divided into smaller overlapping chunks.

Current configuration:

```text
Chunk Size: 500 characters
Overlap: 50 characters
```

The overlap helps preserve contextual information between neighbouring chunks.

```text
Document
│
├── Chunk 0 ───────────────┐
│                          │
│                    50 chars
│                      overlap
│                          │
├────────── Chunk 1 ───────┤
│                          │
│                    50 chars
│                      overlap
│                          │
├────────── Chunk 2 ───────┤
│
└── ...
```

---

# 🔢 3. Embedding Generation

The project uses:

**BAAI/bge-small-en-v1.5**

through the Hugging Face inference API.

```text
Text Chunk
    │
    ▼
BGE-small-en-v1.5
    │
    ▼
384-dimensional Vector
```

Each chunk is represented as a **384-dimensional embedding vector**.

---

# 🗄️ 4. Vector Database

The generated embeddings and associated metadata are stored in **Typesense**.

### Collection

```text
cemk_documents
```

### Schema

```text
chunk_id     → string
text         → string
title        → string
date         → string
type         → string
link         → string
embedding    → float[]
```

The vector field contains 384-dimensional embeddings.

Typesense performs vector similarity search to retrieve the most relevant information for a user query.

---

# 🔍 5. Retrieval Pipeline

The retrieval logic is implemented directly in Python.

```text
User Question
      │
      ▼
Query Embedding
      │
      ▼
Hugging Face
BGE-small-en-v1.5
      │
      ▼
384-dimensional Vector
      │
      ▼
Typesense Vector Search
      │
      ▼
Top 5 Relevant Chunks
```

Current retrieval configuration:

```text
Top K = 5
```

---

# 🤖 6. Answer Generation

Retrieved documents are passed to a Groq-hosted LLM using LangChain.

```text
User Question
      │
      ▼
Retriever
      │
      ▼
Top 5 Documents
      │
      ▼
Context Construction
      │
      ▼
LangChain Prompt
      │
      ▼
Groq LLM
      │
      ▼
Final Answer
```

The generation pipeline follows a **context-only answering strategy**.

The model is instructed to:

* Use only the retrieved context
* Avoid unsupported information
* Give concise answers
* Provide a relevant supporting detail
* Clearly state when the information is unavailable

Fallback response:

```text
I could not find this information in the available data.
```

---

# 📱 7. Telegram AI Assistant

The RAG system is exposed through a Telegram bot using `python-telegram-bot`.

```text
Telegram User
      │
      │ Question
      ▼
Python Telegram Bot
      │
      ▼
generate_answer()
      │
      ▼
retrieve()
      │
      ▼
Typesense
      │
      ▼
Top 5 Context Chunks
      │
      ▼
Groq LLM
      │
      ▼
Generated Answer
      │
      ▼
Telegram Reply
```

---

# 📊 8. RAG Evaluation with LangSmith

The project uses **LangSmith** for tracing and evaluating the RAG pipeline.

The evaluation framework measures four key dimensions:

### Correctness

Checks whether the generated answer matches the expected answer.

### Relevance

Checks whether the answer directly addresses the user's question.

### Groundedness

Checks whether the generated answer is supported by the retrieved context.

### Retrieval Relevance

Checks whether the retrieved documents are relevant to the user's question.

```text
                    Question
                       │
                       ▼
                  RAG Pipeline
                   /       \
                  /         \
                 ▼           ▼
          Retrieved Docs   Answer
                 │           │
                 └─────┬─────┘
                       ▼
                  LangSmith
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   Correctness     Relevance     Groundedness
                       │
                       ▼
              Retrieval Relevance
```

---

# 📁 Project Structure

```text
AI_Powered_University_Update_Information_Assistant/
│
├── .gitignore
├── README.md
├── .python-version
├── pyproject.toml
├── main.py
│
├── data/
│
├── n8n/
│   └── workflow files
│
└── RAG_Pipeline/
    ├── __init__.py
    ├── retriver.py
    ├── generator.py
    ├── bot.py
    └── api.py
```

---

# 🧩 Technology Stack

| Technology            | Purpose                               |
| --------------------- | ------------------------------------- |
| **Python**            | Core application and RAG logic        |
| **n8n**               | Automation and data ingestion         |
| **Hugging Face**      | Embedding generation                  |
| **BGE-small-en-v1.5** | Embedding model                       |
| **Typesense**         | Vector database and similarity search |
| **LangChain**         | LLM integration and prompt pipeline   |
| **Groq**              | LLM inference                         |
| **LangSmith**         | Tracing and evaluation                |
| **Telegram Bot API**  | User interface                        |
| **Git / GitHub**      | Version control                       |

---

# 🔐 Environment Variables

API keys and credentials are stored in a local `.env` file.

Example:

```env
HF_TOKEN=your_huggingface_token
TYPESENSE_API_KEY=your_typesense_key
GROQ_API_KEY=your_groq_key

LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=Rag_College

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

The `.env` file is excluded from Git using `.gitignore`.

**Never commit API keys, tokens, or other credentials to the repository.**

---

# ⚙️ Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd AI_Powered_University_Update_Information_Assistant
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the `.env` file with the required credentials.

---

# ▶️ Running the Application

### Run the Retriever

```bash
python RAG_Pipeline/retriver.py
```

### Run the Generator

```bash
python RAG_Pipeline/generator.py
```

### Run the Telegram Bot

```bash
python RAG_Pipeline/bot.py
```

---

# 🔮 Future Improvements

* PDF document ingestion
* Improved HTML/PDF parsing
* Better chunking strategies
* Metadata filtering
* Hybrid keyword + vector search
* Retrieval reranking
* Automated RAG re-indexing
* Larger evaluation datasets
* Web-based frontend
* Dockerized deployment
* PostgreSQL integration
* MCP-based tool integration
* Advanced monitoring and observability

---

# ⚠️ Disclaimer

This project is an independent AI information assistant built for educational and experimental purposes.

The system retrieves and processes information from publicly accessible institutional sources. Users should verify important information against the original source.

---

# 👨‍💻 Author

**Syed Kaysan Ul Islam**

B.Tech — Artificial Intelligence & Machine Learning

---

## ⭐ Project Highlights

```text
Automated Data Ingestion
        +
RAG
        +
Vector Search
        +
LLM Generation
        +
Telegram Interface
        +
LangSmith Evaluation
```

An end-to-end AI information retrieval system combining **automation, semantic search, LLM generation, and evaluation**.

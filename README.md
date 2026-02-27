# Mortgage Document Intelligence System

A Retrieval-Augmented Generation (RAG) platform that ingests mortgage-related documents — loan applications, closing disclosures, promissory notes, and title reports — and enables underwriters and loan officers to query them using natural language.

---

##  Overview

Mortgage workflows involve reviewing large volumes of semi-structured documents. This system accelerates underwriting and compliance review by:

* Extracting structured and unstructured data from mortgage PDFs
* Indexing content into a semantic vector database
* Enabling natural language Q&A across loan files
* Running automated compliance checks (rules + LLM reasoning)
* Providing a modern web interface for loan teams

---


##  Architecture

```
                ┌──────────────┐
                │   React UI   │
                └──────┬───────┘
                       │
                ┌──────▼───────┐
                │   FastAPI    │
                │   Backend    │
                └──────┬───────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐
│ Document     │ │ RAG       │ │ Compliance  │
│ Processing   │ │ Pipeline  │ │ Engine      │
└───────┬──────┘ └────┬─────┘ └──────┬──────┘
        │              │              │
   PyMuPDF +      LangChain /     Rules + LLM
   pdfplumber     LlamaIndex
                       │
                 ChromaDB /
                  pgvector
                       │
                      LLM
```

---

##  Tech Stack

**Backend**

* FastAPI
* Python 3.10+
* PyMuPDF
* pdfplumber
* LangChain or LlamaIndex
* ChromaDB or pgvector
* OpenAI API or open-source LLMs

**Frontend**

* React
* TypeScript
* Tailwind 

##  Quick Start

### 1️ Clone Repo

```bash
git clone https://github.com/your-org/mortgage-intel.git
cd mortgage-intel
```

---

### 2️ Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Create `.env`:

```env
OPENAI_API_KEY=your_key_here
VECTOR_DB=chroma  # or pgvector
```

Run API:

```bash
uvicorn main:app --reload
```

---

### 3️ Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

App runs at:

* Frontend: http://localhost:5173
* Backend: http://localhost:8000

---

##  Document Ingestion Pipeline

### Steps

1. Upload mortgage PDFs
2. Parse with PyMuPDF + pdfplumber
3. Chunk text intelligently
4. Generate embeddings
5. Store in vector DB
6. Extract key structured fields

### Supported Documents

* Loan Application (1003)
* Closing Disclosure
* Promissory Note
* Title Report
* Appraisal (optional)

---

##  RAG Pipeline

**Flow**

1. User asks question
2. Embed query
3. Retrieve top-k chunks
4. Re-rank (optional)
5. LLM generates grounded answer
6. Return answer + citations


---

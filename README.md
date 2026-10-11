# Smart RAG PDF QA & Information Extraction Platform

## Overview

Smart RAG PDF QA is a Flask-based web application that allows users to upload PDF documents, process and index their contents, and ask natural-language questions. The system uses retrieval-augmented generation (RAG) to produce source-grounded answers with document and page references.

The application supports English and Arabic questions. Answers are generated using a locally hosted language model through Ollama.

## Main Features

- PDF upload and validation
- Text extraction with page-number preservation using PyMuPDF
- Document chunking and indexing
- PostgreSQL storage with pgvector
- Multilingual semantic search using sentence-transformers
- Retrieval-augmented question answering
- Local LLM inference using Ollama
- Arabic question translation for improved retrieval
- Structured answers with source and page citations
- Citation entailment and question relevance checks
- Saved document listing
- Web interface for uploading documents and asking questions
- Automated tests using pytest

## Technology Stack

| Component | Technology |
| --- | --- |
| Backend | Python 3.11, Flask |
| Database | PostgreSQL with pgvector extension |
| ORM | Flask-SQLAlchemy |
| PDF processing | PyMuPDF |
| Embeddings | sentence-transformers |
| Embedding model | intfloat/multilingual-e5-small |
| Vector search | pgvector cosine similarity |
| Local LLM | Ollama with qwen2.5:3b |
| Frontend | HTML, Bootstrap, JavaScript |
| Tests | pytest |

## Prerequisites

- Python 3.11
- PostgreSQL with the pgvector extension installed
- Ollama installed and running
- Ollama model: qwen2.5:3b
- Internet access for the initial embedding model download

The application has been developed and tested locally on Windows.

## Setup on Windows (PowerShell)

### 1. Create a virtual environment

```powershell
py -3.11 -m venv .venv
```

### 2. Install Python dependencies

```powershell
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example configuration:

```powershell
Copy-Item ".env.example" ".env"
```

Edit `.env` and set the correct PostgreSQL username and password.

Configuration variables:

| Variable | Description |
| --- | --- |
| SECRET_KEY | Flask application secret key |
| DATABASE_URL | PostgreSQL connection URL |
| UPLOAD_FOLDER | Directory for uploaded PDF files |
| APP_ENV | Application environment: development or production |

Never commit or distribute a real `.env` file.

### 4. Prepare PostgreSQL

Create a PostgreSQL database named `smartrag` or update `DATABASE_URL` to use your chosen database.

Enable the pgvector extension in the application database:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Initialize the tables in a NEW, EMPTY application database using the included schema.sql file:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d smartrag -X -v ON_ERROR_STOP=1 -f schema.sql
```

The script creates the documents and document_chunks tables and enables pgvector. Do not execute this initialization script against an existing populated database.

### 5. Prepare Ollama

Ensure Ollama is installed and running.

Download the language model:

```powershell
ollama pull qwen2.5:3b
```

Verify that the model is available:

```powershell
ollama list
```

The application expects Ollama to be available locally at:

```text
http://127.0.0.1:11434
```

### 6. Run the application

```powershell
& ".\.venv\Scripts\python.exe" -m flask --app "app:create_app" run --host 127.0.0.1 --port 5000 --no-reload
```

Open:

```text
http://127.0.0.1:5000/
```

## Usage

1. Open the application in a browser.
2. Upload a supported PDF document.
3. Wait for document processing and indexing to finish.
4. Select an indexed document.
5. Ask a question in English or Arabic.
6. Review the generated answer and its source citations.

Answers are intended to be grounded in retrieved PDF content. The system may return no supported answer when sufficient evidence is unavailable.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/` | Main web interface |
| POST | `/api/upload` | Upload and process a PDF |
| GET | `/api/documents` | List saved documents |
| POST | `/api/ask` | Ask a question about an indexed document |

Example JSON request for `/api/ask`:

```json
{
  "document_id": 1,
  "question": "What is the main topic of this document?",
  "top_k": 3
}
```

Replace `document_id` with an ID returned by the application.

## Automated Tests

Run the test suite from the project directory:

```powershell
& ".\.venv\Scripts\python.exe" -m pytest tests -q
```

The verified core test suite can be run with:

```powershell
& ".\.venv\Scripts\python.exe" -m pytest tests -q --tb=line --ignore=tests/test_modality_resolver_feature_safety.py --ignore=tests/test_modality_uncertainty_policy.py
```

At the time of the submission review, 219 core tests passed. Two experimental modality test modules are excluded from this command because seven tests in those modules remain failing. Running the full suite may therefore report failures.

## Known Limitations

- Answer quality depends on PDF text extraction and retrieval quality.
- Relevant passages may not always appear among the top retrieved chunks.
- Language models can occasionally paraphrase numerical values inaccurately.
- Documents containing conflicting information may produce ambiguous answers.
- Citation and relevance checks reduce unsupported responses but do not guarantee correctness.
- Scanned PDFs without extractable text may require OCR support.
- The application is intended for local academic demonstration; production deployment requires additional security and operational review.

## Security and Submission Notes

- Keep `.env` private.
- Use `.env.example` only as a configuration template.
- Do not include uploaded user documents or local database credentials in public repositories.
- Exclude `.venv`, cache files, backups, and experimental artifacts from submission packages.
- The PostgreSQL database and Ollama model must be prepared separately on the target machine.

## Project Status

Academic project implementation with working PDF indexing, semantic retrieval, local LLM question answering, source citations, and a browser-based interface.

## Database schema initialization

Create a new PostgreSQL database named `smartrag` and ensure
that the pgvector extension is available on the PostgreSQL server.

From the project directory, initialize the NEW, EMPTY database:

```powershell
psql -U postgres -d smartrag -v ON_ERROR_STOP=1 -f schema.sql
```

The script creates the `documents` and `document_chunks`
tables, including the 384-dimensional vector column,
foreign key, unique constraint, and indexes.

Update `DATABASE_URL` in your local `.env` to match the
database credentials. Never commit or distribute `.env`.

Do not run `schema.sql` against an existing populated database.

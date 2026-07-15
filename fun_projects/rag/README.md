# RAG Mini Project (Python + FAISS + Sentence Transformers + Ollama)

This project contains a minimal Retrieval-Augmented Generation (RAG) pipeline built with Python.
It demonstrates the core concepts behind embedding documents, storing them in a vector database, retrieving relevant context, and generating responses using a local Large Language Model (LLM) via Ollama.

## Overview

The project implements a simple but complete RAG flow:

1. Load text data from data/raw/texts.txt
2. Generate embeddings using Sentence Transformers
3. Build a FAISS vector index and save it to vectorstore/
4. Receive a user query at runtime
5. Embed the query and run semantic search over the stored documents
6. Provide the retrieved context to a local LLM (Ollama)
7. Generate an answer strictly based on the retrieved information

## Project Structure
```
.
├── data/
│   ├── raw/                 # Input texts
│   └── processed/           # Preprocessed data
├── notebooks/               # Experiments
├── src/                     # Project source code
│   ├── build_index.py       # Create & save FAISS index
│   ├── query_rag.py         # Query RAG pipeline
│   ├── embedder.py          # Embedding model wrapper
│   ├── loaders.py           # Data loading utilities
│   └── utils.py             # Helper functions
├── vectorstore/             # Saved FAISS index
├── models/                  # Local models
├── requirements.txt
└── README.md
```

## Installation
### 1. Clone only the `rag` branch
```bash
git clone -b rag https://github.com/tarmino-dev/thinking.git
cd thinking/fun_projects/rag
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Ollama  
Download and install from:  
https://ollama.com

### 4. Pull a local LLM (for example: gpt-oss:20b)
```bash
ollama pull gpt-oss:20b
```

## Usage
Build the vector index
```bash
python src/build_index.py
```

Query the RAG system
```bash
python src/query_rag.py "your question here"
```

## Technologies Used

- Python
- Sentence Transformers for embeddings
- FAISS for vector search
- LangChain for pipeline components
- Ollama for local LLM inference
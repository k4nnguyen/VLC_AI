# VLC AI - Legal Retrieval-Augmented Generation (RAG) System

**Version:** 1.0.0

## Overview
VLC AI is a specialized Retrieval-Augmented Generation (RAG) application designed to assist users in querying and understanding the Labor Code of Vietnam. The system utilizes advanced natural language processing (NLP) and large language models (LLMs) to retrieve relevant legal articles based on user queries and synthesize accurate, context-aware answers.

## Architecture

The project is structured into several core modules to ensure maintainability, scalability, and high performance:

### 1. Retrieval Module (`src/retrieval`)
The retrieval system is responsible for finding the most relevant legal articles given a user query. It implements a Hybrid RRF (Reciprocal Rank Fusion) approach, combining:
- **Vector Search (Embedding-based):** Captures the semantic meaning of the user query.
- **BM25 Search (Keyword-based):** Ensures exact keyword matches, which is critical in the legal domain where specific terminology matters.
Both results are fused using the RRF algorithm to rank the final results effectively.

### 2. LLM Module (`src/llm`)
This module manages the interaction with Large Language Models (e.g., OpenAI models). It handles prompt building and API communication, ensuring that the retrieved legal context is formatted correctly before being passed to the LLM.

### 3. RAG Core (`src/rag`)
The RAG core orchestrates the entire process:
- **Context Builder:** Aggregates retrieved documents into a coherent context block.
- **Legal RAG Pipeline:** Takes the user query, triggers the retrieval, builds the context, and queries the LLM to generate the final response.

### 4. Verification Module (`src/verification`)
To prevent hallucination, the verification module (`CitationVerifier`) strictly checks the LLM's response against the retrieved legal citations. It ensures that the generated answer does not cite articles or clauses that were not provided in the context.

### 5. Evaluation Module (`src/evaluation`)
A comprehensive suite of evaluation scripts to measure system performance:
- `evaluate.py`: Evaluates retrieval metrics (Recall, Precision, MRR, HitRate) for BM25, Vector, and Hybrid retrievers.
- `generate_evaluation.py`: Uses an LLM to generate a synthetic evaluation dataset (Q&A pairs) from the legal text chunks.
- `evaluate_generation.py`: Evaluates the end-to-end generation quality.
- `evaluate_query_rewrite.py`: (Deprecated) Evaluates the impact of query rewriting on retrieval performance.

## Setup and Installation

### Prerequisites
- Python 3.10+
- `.env` file containing necessary API keys (e.g., `OPENAI_API_KEY`). See `.env.example` for details.

### Installation
Install the required dependencies using pip:
```bash
pip install -r requirements.txt
```

### Database Initialization
Before running the system, initialize the vector and document database:
```bash
python db_init.py
```

## Usage

### Running the Application
Currently, the application can be run via the command line interface:
```bash
python main.py
```

### Running Evaluations
To evaluate the retrieval performance:
```bash
python evaluate.py
```
To generate the evaluation dataset:
```bash
python generate_evaluation.py
```
To evaluate the generation step:
```bash
python evaluate_generation.py
```

## Upcoming Features (Roadmap)
- Integration of a Web Interface using Streamlit.
- Implementation of a RESTful API backend using FastAPI.

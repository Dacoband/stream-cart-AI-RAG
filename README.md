
# StreamCart AI Chatbot Backend

## Overview
This repository contains the backend implementation for an AI-powered chatbot using **LangChain's Retrieval Augmented Generation (RAG)** framework. The chatbot is designed to provide intelligent responses by leveraging indexed data and contextual retrieval.

## Features
- **RAG-based Question Answering**: Uses LangChain's Retrieval Augmented Generation for enhanced AI capabilities.
- **Customizable Prompt Template**: Tailored to StreamCart's specific needs.
- **Data Indexing and Retrieval**: Automatically indexes data from APIs or sample files and retrieves relevant context for answering queries.
- **Greeting Detection**: Friendly responses to common greeting messages.
- **Health Check API**: Verifies system readiness.
- **Data Reindexing API**: Allows dynamic reindexing of data.

## Technologies Used
- **Python**: Core programming language.
- **FastAPI**: Lightweight and fast web framework for building APIs.
- **LangChain**: Framework for creating custom AI chains.
- **Chroma**: Vector database for embedding storage and retrieval.
- **Google Generative AI Embeddings**: Used for embedding and large language model responses.

## Setup Instructions

### Prerequisites
1. Python (>= 3.8)
2. Install dependencies using `pip`.
3. Environment variables:
   - `GOOGLE_API_KEY`
   - `LOGIN_URL`
   - `API_URL`
   - `API_EMAIL`
   - `API_PASSWORD`

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Dacoband/stream-cart-AI-RAG.git
   cd stream-cart-AI-RAG/rag-chatbot
   ```
2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in a `.env` file:
   ```env
   GOOGLE_API_KEY=<your_google_api_key>
   LOGIN_URL=<your_login_url>
   API_URL=<your_api_url>
   API_EMAIL=<your_email>
   API_PASSWORD=<your_password>
   ```

### Running the Application
1. Start the application:
   ```bash
   python main.py
   ```
2. Access the API endpoints:
   - Chat: `POST /api/chat`
   - Health Check: `GET /api/health`
   - Trigger Indexing: `POST /api/index`

## API Endpoints

### 1. Chat Endpoint
**POST `/api/chat`**  
Send a question to the chatbot and receive an answer with sources.

Request:
```json
{
  "question": "What is StreamCart?"
}
```

Response:
```json
{
  "answer": "StreamCart is an AI-powered assistant...",
  "sources": ["Source 1...", "Source 2..."]
}
```

### 2. Health Check
**GET `/api/health`**  
Check the system's readiness status.

Response:
```json
{
  "status": "healthy",
  "rag_chain_ready": true
}
```

### 3. Trigger Indexing
**POST `/api/index`**  
Manually trigger data indexing.

Response:
```json
{
  "message": "Indexing completed successfully"
}
```

## How It Works
1. **Data Indexing**: Fetches data from APIs or sample files and stores embeddings in a Chroma vector database.
2. **Greeting Detection**: Recognizes common greeting messages and provides friendly responses.
3. **Question Answering**: Uses LangChain's RAG framework to retrieve context and provide accurate answers.

## Contribution
Contributions are welcome! Please open an issue or submit a pull request for improvements.



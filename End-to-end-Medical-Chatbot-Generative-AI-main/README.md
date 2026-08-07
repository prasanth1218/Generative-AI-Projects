### Techstack Used:

- Python
- LangChain
- Flask
- GPT
- Pinecone

# 🏥 Medical Chatbot — RAG-based Question Answering System

An end-to-end Retrieval-Augmented Generation (RAG) chatbot that answers medical questions by retrieving relevant context from a curated medical knowledge base and generating grounded, accurate responses using an LLM — instead of relying purely on the model's memorized (and potentially outdated or hallucinated) knowledge.

## 🚀 Overview

This project demonstrates a complete production-style RAG pipeline:

1. **Ingestion** — Medical PDF documents are loaded, split into chunks, and embedded
2. **Storage** — Embeddings are indexed in a Pinecone vector database for fast semantic search
3. **Retrieval** — User queries are embedded and matched against the vector store to find the most relevant context
4. **Generation** — Retrieved context + the user's question are passed to an LLM to generate a grounded answer
5. **Interface** — A Flask web app serves a real-time chat UI

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Orchestration | LangChain |
| Embeddings | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` |
| Vector Database | Pinecone |
| LLM | OpenAI |
| Backend | Flask |
| PDF Parsing | PyPDF |
| Frontend | HTML/CSS (Jinja templates) |

## 📁 Project Structure

```
├── Data/                  # Source medical PDF documents
├── src/
│   ├── helper.py          # PDF loading, text splitting, embedding functions
│   └── prompt.py          # System prompt template
├── static/                # CSS for the chat UI
├── templates/
│   └── chat.html          # Chat interface
├── research/
│   └── trials.ipynb       # Notebook used to prototype the pipeline
├── store_index.py         # One-time script to build the Pinecone index
├── app.py                 # Flask application entry point
├── setup.py
├── template.py
└── requirements.txt
```

## ⚙️ How to Run

### 1. Clone the repository
```bash
git clone https://github.com/prasanth1218/Generative-AI-Projects.git
cd Generative-AI-Projects/End-to-end-Medical-Chatbot-Generative-AI-main
```

### 2. Create a virtual environment
```bash
conda create -n medibot python=3.10 -y
conda activate medibot
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory:
```ini
PINECONE_API_KEY = "your-pinecone-api-key"
OPENAI_API_KEY = "your-openai-api-key"
```

### 5. Build the vector index (one-time setup)
```bash
python store_index.py
```

### 6. Run the app
```bash
python app.py
```

Then open your browser to:
```
http://localhost:8080
```

## 💡 Key Features

- **Grounded answers** — Responses are based on retrieved medical documents, reducing hallucination
- **Semantic search** — Finds the most relevant context using vector similarity rather than keyword matching
- **Modular pipeline** — Ingestion (`store_index.py`) and serving (`app.py`) are cleanly separated
- **Custom prompt engineering** — A dedicated system prompt keeps answers concise and constrained to retrieved context

## 📌 Future Improvements

- Add source citations to responses (which document/page the answer came from)
- Support multi-turn conversational memory
- Add streaming responses for a faster perceived response time
- Deploy to a cloud platform (e.g., Render, AWS)

## 📄 License

This project is licensed under the terms specified in the [LICENSE](./LICENSE) file.

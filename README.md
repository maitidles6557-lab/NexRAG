# NexRAG

NexRAG is a Streamlit app for searching, asking questions about, and summarizing PDF documents with retrieval-augmented generation. It uses Groq for language model calls and downloads its embedding and reranking models from Hugging Face on first startup.

## Deploy on Streamlit Community Cloud

1. Push this project to a GitHub repository. Keep `.env` and `.streamlit/secrets.toml` out of Git; the included `.gitignore` excludes both.
2. In [Streamlit Community Cloud](https://share.streamlit.io/), choose **Create app**, then select the repository, branch, and `app.py` as the entrypoint.
3. In **Advanced settings**, choose Python 3.12 and add the following under **Secrets**:

   ```toml
   GROQ_API_KEY = "your-groq-api-key"
   ```

4. Deploy the app. On first startup it downloads the Hugging Face models, which can take several minutes. The app loads these models into memory, so check the app's available resources if startup fails or the app is evicted.

Streamlit Community Cloud reads the key through `st.secrets`. Never add the real key to a tracked file or paste it into source code. You can update the key later in the app's Streamlit settings.

## Run locally

Requires Python 3.12 and Git. In PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
streamlit run app.py
```

Set `GROQ_API_KEY=...` in `.env`, or create `.streamlit/secrets.toml` with the TOML setting shown above. The app checks Streamlit secrets first and then falls back to environment variables and `.env` for local development.

## Features

- Multi-PDF ingestion through the app's upload controls
- Semantic chunking with a recursive text-splitting fallback
- BGE-large embeddings and ChromaDB vector search
- BM25 keyword and hybrid retrieval with reciprocal rank fusion
- HyDE and multi-query expansion
- Query classification, answer verification, and cross-encoder reranking
- PDF metadata extraction and page citations
- Chat history and multi-document summarization
- Optional contact form email delivery through SMTP

## Configuration

The only required setting is `GROQ_API_KEY`. Optional contact form settings can be added to Streamlit secrets or `.env`:

```toml
CONTACT_EMAIL = "you@example.com"
SMTP_HOST = "smtp.example.com"
SMTP_PORT = 587
SMTP_USERNAME = ""
SMTP_PASSWORD = ""
SMTP_FROM_EMAIL = "you@example.com"
SMTP_USE_TLS = true
SMTP_USE_SSL = false
SMTP_TIMEOUT = 15
```

If SMTP is not configured, the contact form prepares an email draft in the visitor's email app. The account screen stores account records in a local SQLite file; on Streamlit Community Cloud, local files and uploaded documents may be cleared when the app restarts and are not shared or synchronized between instances.

## Project files

```text
app.py                       Streamlit interface and launch point
rag_engine.py                Retrieval, embedding, and generation pipeline
theme.py                     Shared visual theme
assets/nexrag-mark.svg       App mark and favicon
requirements.txt             Python dependencies
.streamlit/config.toml       Streamlit appearance settings
.streamlit/secrets.toml.example  Local secrets template (no real credentials)
```

## Troubleshooting

- **Missing API key:** add `GROQ_API_KEY` to the app's Streamlit settings or your local `.env` file.
- **Slow startup or resource limit errors:** first startup downloads multiple large Hugging Face models. Streamlit Community Cloud has finite CPU and memory resources; review the app resource usage if model loading fails.
- **Dependency build errors:** review the Streamlit deployment logs. The app uses PyTorch, ChromaDB, and sentence-transformers, which can make environment setup slower than a lightweight Streamlit app.
- **Port 8501 is busy locally:** run `streamlit run app.py --server.port 8502`.

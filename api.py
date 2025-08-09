import os
import tempfile
import requests
from typing import List, Tuple, Dict
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import urllib.parse
import time
import logging
import re

from ingest.document_loader import DocumentLoader
from retrieval.vector_store import SimpleVectorStore
from llm.gemini_api import GeminiLLM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="InsureGenie API", version="1.0.0")

security = HTTPBearer()

class HackRxRequest(BaseModel):
    documents: str
    questions: List[str]

class HackRxResponse(BaseModel):
    answers: List[str]

API_KEY = os.getenv("API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError("API_KEY environment variable not set")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY environment variable not set")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K = int(os.getenv("TOP_K_RESULTS", "1"))
SIM_THRESHOLD = float(os.getenv("SIM_THRESHOLD", "0.25"))
ENABLE_SENTENCE_CHUNKING = os.getenv("ENABLE_SENTENCE_CHUNKING", "false").lower() == "true"
ENABLE_SNIPPET_CLEANUP = os.getenv("ENABLE_SNIPPET_CLEANUP", "false").lower() == "true"
CLEAN_SNIPPET_MAX_CHARS = int(os.getenv("CLEAN_SNIPPET_MAX_CHARS", "350"))
DEFAULT_ANSWER_MODE = os.getenv("DEFAULT_ANSWER_MODE", "clause").lower()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials

def download_document(url: str, timeout=10) -> str:
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        temp_dir = tempfile.mkdtemp()
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1] or ".pdf"
        file_path = os.path.join(temp_dir, f"policy{ext}")
        with open(file_path, "wb") as f:
            f.write(response.content)
        return temp_dir
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to download document: {str(e)}")

# Simplified cache: keep only the FAISS index per document URL
DOCUMENT_INDEX_CACHE: Dict[str, SimpleVectorStore] = {}
# Answer cache per (doc_url, question, mode)
ANSWER_CACHE: Dict[Tuple[str, str, str], str] = {}

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
END_PUNCT_RE = re.compile(r"[.!?]\s")

def split_sentences(text: str) -> List[str]:
    return re.split(SENTENCE_SPLIT_RE, text.strip()) if text else []

def chunk_text_simple(text: str, size: int, overlap: int) -> List[str]:
    if size <= 0:
        return [text]
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = max(end - overlap, start + 1)
    return chunks

def chunk_text_sentence_aware(text: str, size: int) -> List[str]:
    sents = split_sentences(text)
    if not sents:
        return [text]
    chunks: List[str] = []
    cur = []
    cur_len = 0
    for s in sents:
        s_len = len(s)
        if cur_len + s_len <= size or not cur:
            cur.append(s)
            cur_len += s_len + 1
        else:
            chunks.append(" ".join(cur).strip())
            cur = [s]
            cur_len = s_len + 1
    if cur:
        chunks.append(" ".join(cur).strip())
    return chunks

def chunk_text(text: str, size: int, overlap: int) -> List[str]:
    if ENABLE_SENTENCE_CHUNKING:
        return chunk_text_sentence_aware(text, size)
    return chunk_text_simple(text, size, overlap)

def concise(text: str, max_chars: int = CLEAN_SNIPPET_MAX_CHARS) -> str:
    t = text.strip()
    if not ENABLE_SNIPPET_CLEANUP:
        if len(t) <= max_chars:
            return t
        end = t.rfind('.', 0, max_chars)
        if end == -1:
            end = max_chars
        return t[:end].strip() + '...'
    if len(t) <= max_chars:
        return t
    start_idx = 0
    first_punct = re.search(r"[A-Z0-9]", t)
    if first_punct:
        start_idx = first_punct.start()
    window = t[start_idx:start_idx + max_chars]
    m = list(END_PUNCT_RE.finditer(window))
    if m:
        end_idx = start_idx + m[-1].end() - 1
    else:
        end_idx = start_idx + max_chars
    return t[start_idx:end_idx].strip() + ('...' if end_idx < len(t) else '')

def build_index_for_dir(temp_dir: str) -> SimpleVectorStore:
    loader = DocumentLoader(temp_dir)
    docs = loader.load_documents()
    raw_texts = [doc.get('text', '') for doc in docs if doc.get('text')]
    texts: List[str] = []
    for t in raw_texts:
        texts.extend(chunk_text(t, CHUNK_SIZE, CHUNK_OVERLAP))
    if not texts:
        raise HTTPException(status_code=400, detail="No text found in the document")
    llm = GeminiLLM()
    if hasattr(llm, 'get_embeddings'):
        embs = llm.get_embeddings(texts)
    else:
        embs = [llm.get_embedding(t) for t in texts]
    dim = int(getattr(embs[0], 'shape', [len(embs[0])])[-1])
    store = SimpleVectorStore(dim=dim)
    for emb, txt in zip(embs, texts):
        store.add(emb, txt)
    return store

def search_top_texts(store: SimpleVectorStore, question: str, llm: GeminiLLM, top_k: int) -> List[str]:
    q_emb = llm.get_embedding(question)
    results = store.search(q_emb, top_k=top_k)
    texts: List[str] = []
    for txt, dist in results:
        try:
            sim = 1.0 - float(dist) / 2.0
        except Exception:
            sim = 0.0
        if sim >= SIM_THRESHOLD:
            texts.append(txt)
    return texts

def compose_answer(question: str, contexts: List[str], llm: GeminiLLM) -> str:
    context_block = "\n---\n".join(contexts[:2])
    prompt_context = f"""
You are an insurance policy assistant. Answer the question in 1-2 sentences (max 80 words) using ONLY the content below. Be precise and natural; don't include citations.

Question: {question}

Context:
{context_block}
"""
    raw = llm.answer_query(question, prompt_context)
    return raw.strip() or concise(contexts[0])

@app.post("/hackrx/run", response_model=HackRxResponse)
async def hackrx_run(request: HackRxRequest, api_key: str = Depends(verify_api_key), answer_mode: str = Header(default=None, alias="X-Answer-Mode")):
    try:
        mode = (answer_mode or DEFAULT_ANSWER_MODE).lower()
        if mode not in ("clause", "compose"):
            mode = "clause"

        if request.documents in DOCUMENT_INDEX_CACHE:
            store = DOCUMENT_INDEX_CACHE[request.documents]
        else:
            temp_dir = download_document(request.documents, timeout=10)
            store = build_index_for_dir(temp_dir)
            DOCUMENT_INDEX_CACHE[request.documents] = store
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

        answers: List[str] = []
        llm = GeminiLLM()
        for question in request.questions:
            cache_key = (request.documents, question.strip().lower(), mode)
            if cache_key in ANSWER_CACHE:
                answers.append(ANSWER_CACHE[cache_key])
                continue

            top_texts = search_top_texts(store, question, llm, top_k=TOP_K if mode == "clause" else max(1, min(2, TOP_K)))
            if not top_texts:
                final = "No relevant content found for this question."
            elif mode == "clause":
                final = concise(top_texts[0])
            else:
                final = compose_answer(question, top_texts, llm)

            ANSWER_CACHE[cache_key] = final
            answers.append(final)

        return HackRxResponse(answers=answers)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("API error")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/v1/hackrx/run", response_model=HackRxResponse)
async def hackrx_run_v1(request: HackRxRequest, api_key: str = Depends(verify_api_key), answer_mode: str = Header(default=None, alias="X-Answer-Mode")):
    return await hackrx_run(request, api_key, answer_mode)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "InsureGenie API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

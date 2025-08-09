from ingest.document_loader import DocumentLoader
from retrieval.vector_store import SimpleVectorStore
from llm.gemini_api import GeminiLLM
import tempfile
import os
import time
import logging

# Use monotonic clock for timeouts
now = time.perf_counter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global cache for embeddings and processed documents
_embedding_cache = {}
_document_cache = {}

# Removed lru_cache to avoid hashing non-hashable LLM instances
def get_cached_embedding(text, llm):
    if text not in _embedding_cache:
        _embedding_cache[text] = llm.get_embedding(text)
    return _embedding_cache[text]

def process_query(uploaded_files, user_query, embedding_dim=768, top_k=1, timeout=14, fast_no_llm=True):
    start_time = now()
    temp_dir = tempfile.mkdtemp()

    try:
        if now() - start_time > timeout:
            return {'answer': 'Processing timeout. Please try again.', 'matched_clauses': [], 'rationale': ''}

        # Save uploaded files to temp dir
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        if now() - start_time > timeout:
            return {'answer': 'Processing timeout. Please try again.', 'matched_clauses': [], 'rationale': ''}

        # Load and limit chunks for speed
        cache_key = f"{temp_dir}_{len(uploaded_files)}"
        if cache_key in _document_cache:
            docs = _document_cache[cache_key]
        else:
            loader = DocumentLoader(temp_dir)
            docs = loader.load_documents()
            _document_cache[cache_key] = docs

        chunks = [doc.get('text', '') for doc in docs if doc.get('text')]
        if not chunks:
            return {'answer': 'No text found in uploaded documents.', 'matched_clauses': [], 'rationale': ''}

        # Cap number of chunks to process (first N pages/sections)
        MAX_CHUNKS = 15
        chunks = chunks[:MAX_CHUNKS]

        llm = GeminiLLM()

        # Batch embeddings for chunks
        if now() - start_time > timeout:
            return {'answer': 'Processing timeout. Please try again.', 'matched_clauses': [], 'rationale': ''}
        if hasattr(llm, 'get_embeddings'):
            import numpy as np
            chunk_embs = llm.get_embeddings(chunks)
        else:
            # Fallback to per-chunk
            chunk_embs = [get_cached_embedding(c, llm) for c in chunks]

        inferred_dim = int(getattr(chunk_embs[0], 'shape', [len(chunk_embs[0])])[-1])

        store = SimpleVectorStore(dim=inferred_dim)
        for emb, chunk in zip(chunk_embs, chunks):
            store.add(emb, chunk)

        if now() - start_time > timeout:
            return {'answer': 'Processing timeout. Please try again.', 'matched_clauses': [], 'rationale': ''}

        query_emb = get_cached_embedding(user_query, llm)
        retrieved = store.search(query_emb, top_k=top_k)
        retrieved_texts = [text for text, _ in retrieved]

        if not retrieved_texts:
            return {'answer': 'Could not find relevant content in the document for your query.', 'matched_clauses': [], 'rationale': ''}

        # Ultra-fast mode: return top clause directly (no LLM)
        if fast_no_llm:
            top_clause = retrieved_texts[0]
            rationale = f"Matched clauses (top {top_k}):\n" + '\n---\n'.join(retrieved_texts)
            return {
                'answer': top_clause,
                'matched_clauses': retrieved_texts,
                'rationale': rationale
            }

        context = '\n---\n'.join(retrieved_texts)

        if now() - start_time > timeout:
            return {'answer': 'Processing timeout. Please try again.', 'matched_clauses': [], 'rationale': ''}

        try:
            answer = llm.answer_query(user_query, context)
        except Exception:
            logger.exception("LLM answer generation failed")
            answer = "Unable to generate an answer right now. Please try again with a more specific question."

        rationale = f"Matched clauses (top {top_k}):\n" + '\n---\n'.join(retrieved_texts)

        processing_time = now() - start_time
        logger.info(f"Processing completed in {processing_time:.2f} seconds")

        return {
            'answer': answer,
            'matched_clauses': retrieved_texts,
            'rationale': rationale
        }

    except Exception as e:
        logger.exception("Processing error")
        msg = str(e) or 'Unknown error (see server logs).'
        return {'answer': f'Error processing request: {msg}', 'matched_clauses': [], 'rationale': ''}
    finally:
        for fname in os.listdir(temp_dir):
            try:
                os.remove(os.path.join(temp_dir, fname))
            except Exception:
                pass
        try:
            os.rmdir(temp_dir)
        except Exception:
            pass

import google.generativeai as genai
import os
import numpy as np
from dotenv import load_dotenv
import time
import logging
from sentence_transformers import SentenceTransformer

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

# Load embedding model once
_EMBED_MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

class GeminiLLM:
    def __init__(self, model_name='gemini-1.5-flash'):
        self.model = genai.GenerativeModel(model_name)

    def extract_entities(self, query):
        prompt = f"""
Extract the following entities from the query: age, procedure, location, policy duration.
Query: {query}
Return as JSON.
"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Entity extraction error: {e}")
            return "{}"

    def get_embeddings(self, texts):
        """Batch embeddings for speed."""
        embs = _EMBED_MODEL.encode(texts, normalize_embeddings=True, batch_size=8, show_progress_bar=False)
        return np.asarray(embs, dtype='float32')

    def get_embedding(self, text):
        # Route through batch path for consistency
        return self.get_embeddings([text])[0]

    def answer_query(self, query, retrieved_chunks):
        """
        Generate answer with optimized prompt.
        """
        try:
            prompt = f"""
Answer this question based on the document clauses:

Question: {query}

Clauses:
{retrieved_chunks}

Provide a concise answer (max 100 words):
"""
            start_time = time.time()
            response = self.model.generate_content(prompt)
            generation_time = time.time() - start_time
            logger.info(f"LLM response generated in {generation_time:.2f}s")
            return (response.text or "").strip()
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return "Unable to generate an answer right now. Please try again with a more specific question."

import faiss
import numpy as np

class SimpleVectorStore:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []
        self.embeddings = []

    def add(self, embedding, text):
        self.index.add(np.array([embedding]).astype('float32'))
        self.texts.append(text)
        self.embeddings.append(embedding)

    def search(self, embedding, top_k=3):
        D, I = self.index.search(np.array([embedding]).astype('float32'), top_k)
        return [(self.texts[i], D[0][idx]) for idx, i in enumerate(I[0]) if i < len(self.texts)]

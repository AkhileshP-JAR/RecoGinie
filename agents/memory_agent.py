import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from vector_store.memory import MemoryStore

class MemoryAgent:
    def __init__(self):
        self.store = MemoryStore()
        loaded = self.store.load_store()
        if not loaded:
            print("WARNING: FAISS store not found. Semantic search won't work.")
            
    def search_similar_movies(self, query, k=3):
        """Search the FAISS vector database for movies matching a text description."""
        try:
            docs = self.store.search_movies(query, k=k)
            return [{"title": d.metadata.get('title'), "genres": d.metadata.get('genres')} for d in docs]
        except Exception as e:
            print(f"Vector search failed: {e}")
            return []

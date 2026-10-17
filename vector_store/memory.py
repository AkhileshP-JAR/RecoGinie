import os
import sys
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data.preprocessing import load_movies

VECTOR_STORE_DIR = os.path.dirname(__file__)
FAISS_INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "faiss_index")

class MemoryStore:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        # Local embeddings to save API calls
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.vector_store = None

    def initialize_store(self, movies_df):
        print("Preparing movie metadata for vectorization...")
        documents = []
        for idx, row in movies_df.iterrows():
            # Build semantic representation of the movie
            # In a real environment, you'd add plot logic here if available.
            # ml-latest-small lacks plot, so using Title + Genres is the best fallback.
            genres = " ".join(row['genres']) if isinstance(row['genres'], list) else str(row['genres']).replace('|', ' ')
            page_content = f"Title: {row['title']}. Genres: {genres}."
            
            doc = Document(
                page_content=page_content,
                metadata={"movieId": row['movieId'], "title": row['title'], "genres": row['genres']}
            )
            documents.append(doc)
            
        print(f"Creating FAISS vector store with {len(documents)} documents. This may take a minute...")
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        self.vector_store.save_local(FAISS_INDEX_PATH)
        print(f"Vector store saved to {FAISS_INDEX_PATH}")

    def load_store(self):
        if os.path.exists(FAISS_INDEX_PATH):
            self.vector_store = FAISS.load_local(FAISS_INDEX_PATH, self.embeddings, allow_dangerous_deserialization=True)
            return True
        return False

    def search_movies(self, query: str, k=5):
        if not self.vector_store:
            raise ValueError("Vector store not initialized/loaded.")
        results = self.vector_store.similarity_search(query, k=k)
        return results

if __name__ == "__main__":
    movies = load_movies()
    movies['genres'] = movies['genres'].str.split('|')
    memory = MemoryStore()
    memory.initialize_store(movies)

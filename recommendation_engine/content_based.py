import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pickle
import os

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

class ContentBasedRecommender:
    def __init__(self):
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.cosine_sim = None
        self.movies_df = None
        self.indices = None

    def fit(self, movies_df):
        """Fit the TF-IDF model and calculate cosine similarity."""
        self.movies_df = movies_df.copy()
        # Clean genres: replace '|' with spaces so TF-IDF can process individual genres
        self.movies_df['genres_str'] = self.movies_df['genres'].apply(
            lambda x: " ".join(x) if isinstance(x, list) else str(x).replace('|', ' ')
        )
        
        # Creating a soup of words from title and genres
        self.movies_df['soup'] = self.movies_df['title'] + " " + self.movies_df['genres_str']
        
        tfidf_matrix = self.tfidf.fit_transform(self.movies_df['soup'])
        self.cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        
        self.indices = pd.Series(self.movies_df.index, index=self.movies_df['title']).drop_duplicates()
        self.save_model()

    def get_similar_items(self, title_or_keyword, top_n=10):
        """Get similar items based on content similarity or keywords."""
        if title_or_keyword not in self.indices:
            # Fallback for keywords (e.g., "Action", "Romance")
            # Search for keyword in the 'soup' column (case-insensitive)
            if self.movies_df is not None and 'soup' in self.movies_df.columns:
                mask = self.movies_df['soup'].str.contains(title_or_keyword, case=False, na=False)
                matches = self.movies_df[mask].copy()
                if not matches.empty:
                    # Return top N matches (perhaps sort by some generic popularity if available, else just top N)
                    matches['similarity_score'] = 1.0 # default score for keyword match
                    return matches.head(top_n)
            return pd.DataFrame()
            
        idx = self.indices[title_or_keyword]
        # Handle case where multiple movies share same title
        if isinstance(idx, pd.Series):
            idx = idx.iloc[0]
            
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        # Skip the original item
        sim_scores = sim_scores[1:top_n+1]
        
        movie_indices = [i[0] for i in sim_scores]
        scores = [i[1] for i in sim_scores]
        
        result = self.movies_df.iloc[movie_indices].copy()
        result['similarity_score'] = scores
        return result

    def get_item_similarity_vector(self, movie_id):
        try:
            idx = self.movies_df[self.movies_df['movieId'] == movie_id].index[0]
            return self.cosine_sim[idx]
        except IndexError:
            return None

    def save_model(self):
        path = os.path.join(MODEL_DIR, "cb_model.pkl")
        with open(path, "wb") as f:
            pickle.dump({'sim': self.cosine_sim, 'movies': self.movies_df, 'indices': self.indices}, f)
            
    def load_model(self):
        path = os.path.join(MODEL_DIR, "cb_model.pkl")
        if os.path.exists(path):
            with open(path, "rb") as f:
                data = pickle.load(f)
                self.cosine_sim = data['sim']
                self.movies_df = data['movies']
                self.indices = data['indices']
            return True
        return False

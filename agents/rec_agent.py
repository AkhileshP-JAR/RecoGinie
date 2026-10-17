import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from recommendation_engine.hybrid import HybridRecommender

class RecommendationAgent:
    def __init__(self):
        self.engine = HybridRecommender()
        loaded = self.engine.load_models()
        if not loaded:
            print("WARNING: Recommendation models could not be loaded. Please run train_models.py")

    def get_recommendations(self, user_id, movie_title_hint=None, top_n=3):
        """
        In a real app, user_id would map to the integer Matrix Factorization ID.
        Here we use a random fallback if they are entirely new, or utilize the `movie_title_hint`.
        """
        # We will attempt to use user_id as an integer if possible, else 0 (fallback)
        try:
            numeric_uid = int(user_id)
        except ValueError:
            numeric_uid = 999999 # completely unseen
            
        # Fetch a slightly larger pool to allow random selection so recommendations change on each click
        pool_size = top_n * 3
        recommendations = self.engine.recommend(user_id=numeric_uid, movie_title=movie_title_hint, top_n=pool_size)
        
        # Shuffle/sample to provide variety
        if not recommendations.empty:
            recommendations = recommendations.sample(n=min(top_n, len(recommendations)))
        
        # Return format expected by the conversation logic
        results = []
        for idx, row in recommendations.iterrows():
            results.append({
                "movieId": row['movieId'],
                "title": row['title'],
                "genres": row['genres']
            })
        return results

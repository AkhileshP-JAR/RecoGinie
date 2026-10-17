import pandas as pd
from .collaborative import CollaborativeRecommender
from .content_based import ContentBasedRecommender

class HybridRecommender:
    def __init__(self, cf_weight=0.5, cb_weight=0.5):
        self.cf_model = CollaborativeRecommender()
        self.cb_model = ContentBasedRecommender()
        self.cf_weight = cf_weight
        self.cb_weight = cb_weight

    def load_models(self):
        """Load both pre-trained models. Returns True if successful."""
        cf_loaded = self.cf_model.load_model()
        cb_loaded = self.cb_model.load_model()
        return cf_loaded and cb_loaded

    from functools import lru_cache
    @lru_cache(maxsize=128)
    def recommend(self, user_id, movie_title=None, top_n=10):
        """
        Recommend movies using a hybrid approach.
        If user_id is mostly new, rely more on Content-Based (if movie_title is provided).
        """
        # Get Collaborative predictions
        cf_preds = self.cf_model.get_user_predictions(user_id)
        
        # If user has no history, we depend entirely on CB or return populars
        if cf_preds.empty and not movie_title:
            # Fallback to popular movies (naive approach for cold start)
            return self.get_popular_movies(top_n)
            
        cb_recommendations = None
        if movie_title:
            cb_recommendations = self.cb_model.get_similar_items(movie_title, top_n=top_n)

        # Basic weighting logic: 
        # If we have both, we take the top N from CF, find their content similarity to the user's liked movies, etc.
        # Alternatively, we just return CF as primary, interleaved with CB if they specify a movie
        
        results = []
        if not cf_preds.empty:
            cf_top = cf_preds.sort_values(ascending=False).head(top_n*2)
            # Find matching movie records
            movies_df = self.cb_model.movies_df
            if movies_df is not None:
                cf_movies = movies_df[movies_df['movieId'].isin(cf_top.index)].copy()
                # Dummy score to keep the order
                cf_movies['hybrid_score'] = cf_movies['movieId'].map(cf_top) * self.cf_weight
                results.append(cf_movies)

        if cb_recommendations is not None and not cb_recommendations.empty:
            cb_recommendations['hybrid_score'] = cb_recommendations['similarity_score'] * self.cb_weight
            results.append(cb_recommendations)

        if not results:
            return self.get_popular_movies(top_n)

        final_df = pd.concat(results).drop_duplicates(subset=['movieId'])
        final_df = final_df.sort_values(by='hybrid_score', ascending=False).head(top_n)
        
        return final_df

    def get_popular_movies(self, top_n=10):
        # As a fallback
        if self.cb_model.movies_df is not None:
            return self.cb_model.movies_df.head(top_n)
        return pd.DataFrame()

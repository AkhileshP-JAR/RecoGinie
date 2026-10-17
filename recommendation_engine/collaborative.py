import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
import pickle
import os

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

class CollaborativeRecommender:
    def __init__(self, n_components=50):
        self.n_components = n_components
        self.model = TruncatedSVD(n_components=self.n_components, random_state=42)
        self.user_item_matrix = None
        self.user_index = None
        self.item_index = None
        self.predictions = None

    def fit(self, ratings_df):
        """Fit the collaborative filtering model using TruncatedSVD."""
        # Create user-item matrix
        self.user_item_matrix = ratings_df.pivot(index='userId', columns='movieId', values='rating').fillna(0)
        self.user_index = self.user_item_matrix.index
        self.item_index = self.user_item_matrix.columns
        
        # Apply SVD
        matrix = self.user_item_matrix.values
        user_factors = self.model.fit_transform(matrix)
        item_factors = self.model.components_
        
        # Reconstruct matrix
        self.predictions = pd.DataFrame(
            np.dot(user_factors, item_factors), 
            index=self.user_index, 
            columns=self.item_index
        )
        
        self.save_model()

    def get_user_predictions(self, user_id):
        """Get prediction scores for a user."""
        if user_id not in self.predictions.index:
            return pd.Series(dtype=float)
        return self.predictions.loc[user_id]

    def save_model(self):
        path = os.path.join(MODEL_DIR, "cf_model.pkl")
        with open(path, "wb") as f:
            pickle.dump(self.predictions, f)
            
    def load_model(self):
        path = os.path.join(MODEL_DIR, "cf_model.pkl")
        if os.path.exists(path):
            with open(path, "rb") as f:
                self.predictions = pickle.load(f)
                return True
        return False

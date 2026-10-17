import os
import sys

# Add parent dir to path so we can import from data and recommendation_engine
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data.preprocessing import preprocess_data
from recommendation_engine.collaborative import CollaborativeRecommender
from recommendation_engine.content_based import ContentBasedRecommender

def main():
    print("Loading datasets...")
    movies, ratings, merged_df = preprocess_data()
    
    # Train CF
    print(f"Training Collaborative Filtering Model on {len(ratings)} user ratings...")
    cf_recommender = CollaborativeRecommender(n_components=50)
    cf_recommender.fit(ratings)
    print("CF Model trained and saved.")

    # Train CB
    print(f"Training Content-Based Filtering Model on {len(movies)} movies...")
    cb_recommender = ContentBasedRecommender()
    cb_recommender.fit(movies)
    print("CB Model trained and saved.")

if __name__ == "__main__":
    main()

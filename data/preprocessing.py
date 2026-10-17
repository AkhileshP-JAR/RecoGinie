import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml-latest-small")

def load_movies():
    """Load the movies.csv dataset."""
    movies_path = os.path.join(DATA_DIR, "movies.csv")
    if not os.path.exists(movies_path):
        raise FileNotFoundError(f"Dataset not found at {movies_path}. Please extract ml-latest-small.")
    return pd.read_csv(movies_path)

def load_ratings():
    """Load the ratings.csv dataset."""
    ratings_path = os.path.join(DATA_DIR, "ratings.csv")
    if not os.path.exists(ratings_path):
        raise FileNotFoundError(f"Dataset not found at {ratings_path}.")
    return pd.read_csv(ratings_path)

def load_tags():
    """Load the tags.csv dataset."""
    tags_path = os.path.join(DATA_DIR, "tags.csv")
    if not os.path.exists(tags_path):
        raise FileNotFoundError(f"Dataset not found at {tags_path}.")
    return pd.read_csv(tags_path)

def preprocess_data():
    """
    Preprocess and merge necessary data for modeling.
    Returns:
        pd.DataFrame: Merged data ready for analysis.
    """
    movies = load_movies()
    ratings = load_ratings()
    
    # Example: we can merge ratings and movies
    # Extract year from title if needed
    movies['year'] = movies['title'].str.extract(r'\((\d{4})\)$')
    movies['genres'] = movies['genres'].str.split('|')
    
    merged_data = pd.merge(ratings, movies, on='movieId', how='left')
    return movies, ratings, merged_data

if __name__ == "__main__":
    movies, ratings, merged_df = preprocess_data()
    print(f"Loaded {len(movies)} movies and {len(ratings)} ratings.")
    print("Movies preview:")
    print(movies.head())

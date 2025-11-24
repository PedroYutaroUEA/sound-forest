import os


class Config:
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ITEMS_FILE = os.path.join(DATA_DIR, "new_items.csv")
    RATINGS_FILE = os.path.join(DATA_DIR, "new_ratings_dense.csv")
    GENRE_WEIGHTS_FILE = os.path.join(DATA_DIR, "genre_weights.json")

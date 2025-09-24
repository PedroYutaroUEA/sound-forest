import pandas as pd
import numpy as np

RATINGS_PATH = "../data/ratings.csv"
ITEMS_PATH = "../data/items.csv"


class RecommendationService:
    def __init__(self):
        self.rattings = pd.read_csv(RATINGS_PATH)
        self.items = pd.read_csv(ITEMS_PATH)

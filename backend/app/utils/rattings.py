import pandas as pd

from app.config import Config


def load_ratings():
    return pd.read_csv(Config.RATINGS_FILE)


def save_ratings(df):
    df.to_csv(Config.RATINGS_FILE, index=False)

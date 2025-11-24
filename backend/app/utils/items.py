import pandas as pd

from app.config import Config


def load_items():
    return pd.read_csv(Config.ITEMS_FILE)

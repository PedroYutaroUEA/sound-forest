import os
import json

from app.config import Config


def load_genre_weights():
    if os.path.exists(Config.GENRE_WEIGHTS_FILE):
        with open(Config.GENRE_WEIGHTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_genre_weights(d):
    with open(Config.GENRE_WEIGHTS_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f)

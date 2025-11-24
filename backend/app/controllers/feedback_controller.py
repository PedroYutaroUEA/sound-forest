from app.models.feedback import Feedback
from app.utils import (
    load_genre_weights,
    load_items,
    load_ratings,
    save_ratings,
    save_genre_weights,
)
import pandas as pd


class FeedbackController:
    def handle_feedback(self, fb: Feedback):
        ratings = load_ratings()
        new_row = {
            "user_id": int(fb.user_id),
            "item_id": int(fb.item_id),
            "rating": int(fb.rating),
        }
        ratings = pd.concat([ratings, pd.DataFrame([new_row])], ignore_index=True)
        save_ratings(ratings)

        # Atualizar pesos de gênero (incremental + decay)
        items = load_items()
        item_row = items[items.id == fb.item_id]

        if not item_row.empty:
            genre = str(item_row.iloc[0].genre)
            gw = load_genre_weights()

            # positiva (4–5) aumenta peso
            if fb.rating >= 4:
                delta = (fb.rating - 3) * 0.02
                gw[genre] = gw.get(genre, 0.0) * 0.9 + delta

            # negativa (1–2) reduz peso
            elif fb.rating <= 2:
                delta = (3 - fb.rating) * 0.02
                gw[genre] = gw.get(genre, 0.0) * 0.9 - delta

            # limitar intervalo [0,1]
            if gw[genre] < 0.0:
                gw[genre] = 0.0
            if gw[genre] > 1.0:
                gw[genre] = 1.0

            save_genre_weights(gw)

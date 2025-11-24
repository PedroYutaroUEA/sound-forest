from app.models.simulate_request import SimulateRequest
from app.utils import load_items, load_ratings, save_ratings, save_genre_weights
import pandas as pd


class UserSimulationController:
    def __init__(self):
        self.items = load_items()
        self.ratings = load_ratings()

    def __pick_songs(self, user_id, body, random_state) -> list:
        rows = []
        for g in body.genres:
            choices = self.items[self.items.genre == g]
            if choices.empty:
                continue
            sample = choices.sample(min(5, len(choices)), random_state=random_state)
            for _, row in sample.iterrows():
                rows.append(
                    {"user_id": int(user_id), "item_id": int(row.id), "rating": 5}
                )
        return rows

    def get_first_recommendation(
        self, body: SimulateRequest, random_state: int | None = None
    ):

        # new user id
        if self.ratings.empty:
            new_id = 1
        else:
            new_id = int(self.ratings.user_id.max()) + 1

        # pick até 5 músicas de cada gênero escolhido e dar nota inicial 5
        new_rows = self.__pick_songs(
            user_id=new_id, body=body, random_state=random_state
        )

        if new_rows:
            self.ratings = pd.concat(
                [self.ratings, pd.DataFrame(new_rows)], ignore_index=True
            )
            save_ratings(self.ratings)

        initial_weights = {g: 0.05 for g in body.genres}
        save_genre_weights(initial_weights)

        return {"user_id": new_id, "status": "simulated"}

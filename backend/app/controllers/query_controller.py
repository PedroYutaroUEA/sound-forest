from app.utils.items import load_items
from app.utils.rattings import load_ratings


class QueryController:
    def get_all_genres(self):
        items = load_items()
        return sorted(items.genre.dropna().unique().tolist())

    def get_all_users_ids(self):
        ratings = load_ratings()
        return sorted(ratings.user_id.unique().tolist())

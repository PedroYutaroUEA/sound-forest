from app.services.recommendation_service import RecommendationService
from app.utils import load_items, load_ratings, load_genre_weights


class RecommendationController:
    def __init__(self, user_id: int, n: int, metric):
        self.user_id = user_id
        self.n = n
        self.metric = metric
        self.recommendation_service = RecommendationService(self.metric)

    def recommend(self):
        items = load_items()
        ratings = load_ratings()
        gw = load_genre_weights()
        recs = self.recommendation_service.recommend_items(
            user_id=self.user_id,
            n=self.n,
            ratings_df=ratings,
            items_df=items,
            genre_weights=gw,
            max_items_to_check=3000,
        )
        return {"user_id": self.user_id, "recommendations": recs}

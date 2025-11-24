from app.services.recommendation_service import RecommendationService
from app.utils import load_ratings, load_genre_weights, load_items
import numpy as np

TOTAL_ITEMS = 9564


class AccuracyController:
    def __init__(self, metric):
        self.recommendation_service = RecommendationService(metric)
        self.ratings = load_ratings()
        self.gw = load_genre_weights()
        self.items = load_items()

    def __compute_accuracy(self, user_id, n_recommend, test_frac):
        user_r = self.ratings[self.ratings.user_id == user_id]
        liked = user_r[user_r.rating >= 4]
        if len(liked) < 1:
            return {
                "user_id": user_id,
                "accuracy": None,
                "reason": "poucos itens curtidos para teste",
            }

        test = liked.sample(max(1, int(len(liked) * test_frac)))
        train = self.ratings.drop(test.index)

        n_chances = max(n_recommend, 100)

        recs_full = self.recommendation_service.recommend_items(
            user_id,
            n=n_chances,
            ratings_df=train,
            items_df=self.items,
            genre_weights=self.gw,
            max_items_to_check=TOTAL_ITEMS,
        )

        recs = recs_full[:n_recommend]

        rec_ids = set([r["item_id"] for r in recs])

        hits = sum(1 for iid in test.item_id if iid in rec_ids)

        acc = hits / len(recs) if len(recs) > 0 else 0.0

        return {
            "user_id": user_id,
            "hits": int(hits),
            "recommended": len(recs),
            "accuracy": acc,
        }

    def get_accuracy(
        self, user_id: int, n_recommend: int, test_frac: float, max_users: int
    ) -> dict:
        if user_id is not None:
            return self.__compute_accuracy(
                user_id=user_id, n_recommend=n_recommend, test_frac=test_frac
            )
        else:
            users = self.ratings.user_id.unique().tolist()

            # escolher apenas até max_users usuários (aleatórios)
            if len(users) > max_users:
                users = list(np.random.choice(users, size=max_users, replace=False))

            accs = []
            for u in users:
                res = self.__compute_accuracy(
                    user_id=int(u), n_recommend=n_recommend, test_frac=test_frac
                )
                if res.get("accuracy") is not None:
                    accs.append(res["accuracy"])

            mean_acc = float(np.mean(accs)) if accs else None
            return {
                "mean_accuracy": mean_acc,
                "n_users_evaluated": len(accs),
                "max_users": max_users,
            }

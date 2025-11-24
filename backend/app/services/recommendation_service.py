import time
from app.services.prediction_service import PredictionService
from app.utils import logger


class RecommendationService:
    def __init__(self, metric):
        self.prediction_service = PredictionService(metric=metric)

    def __predict_rating(
        self,
        ratings_df,
        user_id,
        item_id,
        user_item_dict,
        user_means,
        sim_cache,
        item_to_ratings,
    ):
        """Predição de nota para (user,item) usando Pearson + cache."""
        global_mean = ratings_df.rating.mean() if not ratings_df.empty else 3.0
        user_mean = user_means.get(user_id, global_mean)

        if item_id not in item_to_ratings:
            return user_mean

        num, den = 0.0, 0.0
        for other_user, other_rating in item_to_ratings[item_id]:
            if other_user == user_id:
                continue
            sim = self.prediction_service.predict(
                user_id, other_user, user_item_dict, sim_cache
            )
            if sim == 0:
                continue
            other_mean = user_means.get(other_user, global_mean)
            num += sim * (other_rating - other_mean)
            den += abs(sim)

        if den == 0:
            return user_mean
        return user_mean + (num / den)

    def recommend_items(
        self,
        user_id,
        n=10,
        ratings_df=None,
        items_df=None,
        genre_weights=None,
        max_items_to_check=5000,
    ) -> list:
        start = time.time()

        logger.info(f"recommend_items start user_id={user_id} n={n}")

        # Pré-computações
        user_item_dict = {}
        user_means = {}
        item_to_ratings = {}

        for uid, g in ratings_df.groupby("user_id"):
            d = dict(zip(g["item_id"], g["rating"]))
            user_item_dict[int(uid)] = d
            user_means[int(uid)] = float(g["rating"].mean())

        for iid, g in ratings_df.groupby("item_id"):
            item_to_ratings[int(iid)] = list(
                zip(g["user_id"].astype(int), g["rating"].astype(float))
            )

        rated_items = set(ratings_df[ratings_df.user_id == user_id].item_id.tolist())
        candidates = []
        sim_cache = {}

        # Cold-start: gêneros curtidos
        liked_items = ratings_df[
            (ratings_df.user_id == user_id) & (ratings_df.rating >= 4)
        ].item_id.tolist()
        liked_genres = (
            items_df[items_df.id.isin(liked_items)].genre.unique().tolist()
            if liked_items
            else []
        )

        # Amostra para acelerar

        total_items = len(items_df)
        sample_size = min(
            max_items_to_check if max_items_to_check else total_items, total_items
        )
        items_sample = items_df.sample(
            n=sample_size, random_state=int(time.time() * 1000) % 10000
        ).to_dict(orient="records")

        # Calcular predições
        for item in items_sample:
            item_id = int(item["id"])
            if item_id in rated_items:
                continue
            base_pred = self.__predict_rating(
                ratings_df,
                user_id,
                item_id,
                user_item_dict,
                user_means,
                sim_cache,
                item_to_ratings,
            )
            genre = str(item["genre"])
            weight = float(genre_weights.get(genre, 0.0))

            max_boost = 0.05  # máximo 5% de aumento
            applied_boost = min(weight, max_boost)
            score = base_pred * (1.0 + applied_boost)

            candidates.append(
                {
                    "item_id": item_id,
                    "title": item["title"],
                    "artist": item.get("artist", ""),
                    "genre": genre,
                    "score": float(score),
                    "base_pred": float(base_pred),
                }
            )

        candidates.sort(key=lambda x: x["score"], reverse=True)

        # Diversidade no cold-start: sempre incluir 1 item de outro gênero
        if (not any(genre_weights.values())) or (len(liked_items) <= 2):
            top = candidates[: max(0, n - 1)]
            other_pool = items_df[
                ~items_df.genre.isin(liked_genres) & ~items_df.id.isin(rated_items)
            ]
            if not other_pool.empty:
                surprise = other_pool.sample(
                    n=1, random_state=int(time.time() % 10000)
                ).iloc[0]
                surprise_rec = {
                    "item_id": int(surprise.id),
                    "title": surprise.title,
                    "artist": getattr(surprise, "artist", ""),
                    "genre": str(surprise.genre),
                    "score": float(0.5),
                    "base_pred": float(0.5),
                }
                final = top[: n - 1] + [surprise_rec]
                elapsed = time.time() - start
                logger.info(
                    f"recommend_items finished user_id={user_id} time={elapsed:.3f}s (cold-start with surprise)"
                )
                return final

        elapsed = time.time() - start
        logger.info(f"recommend_items finished user_id={user_id} time={elapsed:.3f}s")
        return candidates[:n]

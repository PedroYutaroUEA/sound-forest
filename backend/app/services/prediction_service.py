import numpy as np


class PredictionService:
    def __init__(self, metric: str | None = "cossin"):
        self.metric = metric

    def predict(self, u1, u2, user_item_dict, sim_cache) -> float:
        pred = 0.0
        if self.metric == "cossin":
            pred += self.__cosine_similarity(u1, u2, user_item_dict, sim_cache)
        elif self.metric == "pearson":
            pred += self.__pearson_correlation(u1, u2, user_item_dict, sim_cache)
        return pred

    def __pearson_correlation(self, u1, u2, user_item_dict, sim_cache):
        """Calcula Pearson entre u1 e u2 usando dicionários user->items.
        Usa cache para evitar recomputação."""
        key = tuple(sorted((int(u1), int(u2))))
        if key in sim_cache:
            return sim_cache[key]

        u1_items = user_item_dict.get(u1, {})
        u2_items = user_item_dict.get(u2, {})
        common = set(u1_items.keys()).intersection(u2_items.keys())
        if len(common) < 2:
            sim_cache[key] = 0.0
            return 0.0

        r1 = np.array([u1_items[i] for i in common], dtype=float)
        r2 = np.array([u2_items[i] for i in common], dtype=float)
        r1m = r1.mean()
        r2m = r2.mean()

        num = ((r1 - r1m) * (r2 - r2m)).sum()
        den = np.sqrt(((r1 - r1m) ** 2).sum() * ((r2 - r2m) ** 2).sum())
        sim = float(num / den) if den != 0 else 0.0
        sim_cache[key] = sim
        return sim

    def __cosine_similarity(self, u1, u2, user_item_dict, sim_cache):
        """Calcula Similaridade de Cossenos (mais robusta para esparsidade)."""
        key = tuple(sorted((int(u1), int(u2))))
        if key in sim_cache:
            return sim_cache[key]

        u1_items = user_item_dict.get(u1, {})
        u2_items = user_item_dict.get(u2, {})
        common = set(u1_items.keys()).intersection(u2_items.keys())

        if len(common) < 1:  # Cossenos precisa de apenas 1 item em comum.
            sim_cache[key] = 0.0
            return 0.0

        r1 = np.array([u1_items[i] for i in common], dtype=float)
        r2 = np.array([u2_items[i] for i in common], dtype=float)

        dot_product = np.dot(r1, r2)
        norm_u1 = np.linalg.norm(r1)
        norm_u2 = np.linalg.norm(r2)

        if norm_u1 == 0 or norm_u2 == 0:
            sim_cache[key] = 0.0
            return 0.0

        sim = float(dot_product / (norm_u1 * norm_u2))
        sim_cache[key] = sim
        return sim

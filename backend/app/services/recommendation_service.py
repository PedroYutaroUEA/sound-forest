from math import sqrt
import pandas as pd
import numpy as np

RATINGS_PATH = "../data/ratings.csv"
ITEMS_PATH = "../data/items.csv"


# A IMPLEMENTAR:
# - A RECOMENDAÇÃO DE FATO
# - A METRICA QUE VAI SER UTILIZADA
# - CALCULO DA ACURACIA DA RECOMENDAÇÃO (NEM SEI SE VAI SER AI)


class RecommendationService:
    def __init__(self):
        self.ratings = pd.read_csv(RATINGS_PATH)
        self.items = pd.read_csv(ITEMS_PATH)
        self.user_item_matrix = self._create_user_item_matrix()
        self.item_similarity_matrix = self._create_item_similarity_matrix()

    def _create_user_item_matrix(self):
        # Transforma os dados de avaliações em uma matriz de usuário-item
        return self.ratings.pivot_table(
            index="user_id", columns="item_id", values="rating"
        ).fillna(0)

    def _create_item_similarity_matrix(self):
        # Calcula a similaridade entre os itens usando a matriz transposta
        item_vectors = self.user_item_matrix.T
        item_sim_matrix = ALGUMA_METRICA_AI(item_vectors)
        # Cria um DataFrame para facilitar o acesso
        return pd.DataFrame(
            item_sim_matrix, index=item_vectors.index, columns=item_vectors.index
        )

    def first_recommendation(self, genres: list, n_recommendations=5) -> list:
        initial_items = self.items[self.items["genero_principal"].isin(genres)]

        if initial_items.empty:
            return []

        return initial_items.sample(
            n=min(n_recommendations, len(initial_items))
        ).to_dict(orient="records")

    def __pearson(self, rating1, rating2):
        sum_xy = 0
        sum_x = 0
        sum_y = 0
        sum_x2 = 0
        sum_y2 = 0
        n = 0
        for key in rating1:
            if key in rating2:
                n += 1
                x = rating1[key]
                y = rating2[key]
                sum_xy += x * y
                sum_x += x
                sum_y += y
                sum_x2 += pow(x, 2)
                sum_y2 += pow(y, 2)
        denominator = sqrt(sum_x2 - pow(sum_x, 2) / n) * sqrt(
            sum_y2 - pow(sum_y, 2) / n
        )
        if denominator == 0:
            return 0
        else:
            return (sum_xy - (sum_x * sum_y) / n) / denominator

    def computeNearestNeighbor(self, target, all_rattings):
        distances = []
        current_user_ratings = (
            all_rattings[all_rattings["target"] == target]
            .set_index("Game")["Rating"]
            .to_dict()
        )

        for user in all_rattings["target"].unique():
            if user != target:
                other_user_ratings = (
                    all_rattings[all_rattings["target"] == user]
                    .set_index("Game")["Rating"]
                    .to_dict()
                )
                distance = self.__pearson(current_user_ratings, other_user_ratings)
                distances.append((distance, user))

        distances.sort(reverse=True)
        return distances

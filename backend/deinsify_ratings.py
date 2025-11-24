import pandas as pd
import numpy as np
import os

# --- Configurações do Script ---
RATINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ratings.csv")
TARGET_ROWS = 10000  # Queremos um total de aproximadamente 10.000 linhas
MAX_ITEM_ID = 114000  # Seu catálogo tem 114.000 itens


def densify_ratings_dataset():
    """
    Carrega o ratings.csv, identifica os usuários existentes e adiciona avaliações
    aleatórias a esses usuários até atingir o volume desejado.
    """
    try:
        # 1. Carregar o dataset existente
        ratings_df = pd.read_csv(RATINGS_FILE)
        print(f"Linhas iniciais no ratings.csv: {len(ratings_df)}")

        existing_users = ratings_df["user_id"].unique().tolist()
        num_existing_users = len(existing_users)

        # 2. Calcular quantas novas linhas precisamos
        current_rows = len(ratings_df)
        rows_to_add = TARGET_ROWS - current_rows

        if rows_to_add <= 0:
            print("O dataset já tem 10.000 linhas ou mais. Nenhuma ação necessária.")
            return

        print(f"Número de usuários mantidos: {num_existing_users}")
        print(f"Novas avaliações a serem geradas: {rows_to_add}")

    except FileNotFoundError:
        print(
            f"Arquivo {RATINGS_FILE} não encontrado. Certifique-se de que o caminho está correto."
        )
        return

    new_ratings = []

    # 3. Gerar as novas avaliações, distribuindo-as entre os usuários existentes

    # Distribui o número de novas avaliações igualmente entre os usuários
    ratings_per_user = rows_to_add // num_existing_users
    remaining_ratings = rows_to_add % num_existing_users

    # 4. Loop para adicionar as novas avaliações
    for user_id in existing_users:

        # O usuário fará a cota base + 1 se for um dos 'restantes'
        num_ratings_for_user = ratings_per_user + (1 if remaining_ratings > 0 else 0)
        if remaining_ratings > 0:
            remaining_ratings -= 1

        # Garante que não adicionamos avaliações duplicadas
        rated_items = set(ratings_df[ratings_df.user_id == user_id]["item_id"])

        # Seleciona itens não avaliados aleatoriamente
        possible_items = list(set(range(1, MAX_ITEM_ID + 1)) - rated_items)

        # Limita para o número de itens disponíveis
        items_to_rate = min(num_ratings_for_user, len(possible_items))

        if items_to_rate > 0:
            item_ids = np.random.choice(
                possible_items, size=items_to_rate, replace=False
            )

            # Gera notas aleatórias (de 1 a 5)
            ratings = np.random.randint(1, 6, size=items_to_rate)

            for item_id, rating in zip(item_ids, ratings):
                new_ratings.append(
                    {"user_id": user_id, "item_id": item_id, "rating": rating}
                )

    # 5. Concatenar e salvar
    if new_ratings:
        new_df = pd.DataFrame(new_ratings)
        ratings_df = pd.concat([ratings_df, new_df], ignore_index=True)

    ratings_df.to_csv(RATINGS_FILE, index=False)
    print("---")
    print(f"Dataset densificado com sucesso!")
    print(f"Total final de linhas no ratings.csv: {len(ratings_df)}")
    print(f"Número de usuários mantidos: {num_existing_users}")


if __name__ == "__main__":
    densify_ratings_dataset()

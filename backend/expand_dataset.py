import pandas as pd
import numpy as np
import os

# --- Configurações do Script ---
RATINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ratings.csv")
TARGET_ROWS = 5000  # Queremos atingir cerca de 5000 linhas
MIN_ITEM_ID = 1  # ID do item começa em 1
MAX_ITEM_ID = 114000  # Seu catálogo tem 114.000 itens
NEW_USERS_TO_ADD = 1000  # Adicionar 1000 novos usuários
MAX_RATINGS_PER_NEW_USER = 5  # Avaliar no máximo 5 itens por novo usuário (para manter um pouco de esparsidade)


def expand_ratings_dataset():
    """
    Carrega o ratings.csv existente e adiciona novas linhas de avaliações aleatórias.
    """
    try:
        # 1. Carregar o dataset existente
        ratings_df = pd.read_csv(RATINGS_FILE)
        print(f"Linhas iniciais no ratings.csv: {len(ratings_df)}")

        # 2. Definir o próximo ID de usuário (começa após o máximo existente)
        max_existing_user = ratings_df["user_id"].max()
        start_user_id = max_existing_user + 1
        print(f"Próximo ID de usuário a ser gerado: {start_user_id}")

    except FileNotFoundError:
        print(f"Arquivo {RATINGS_FILE} não encontrado. Crie um ratings.csv básico.")
        return
    except KeyError:
        print(
            "Certifique-se de que seu ratings.csv tem as colunas 'user_id', 'item_id', 'rating'."
        )
        return

    new_ratings = []

    # 3. Gerar novos usuários
    for user_id in range(start_user_id, start_user_id + NEW_USERS_TO_ADD):
        # Número aleatório de avaliações que este usuário fará
        num_ratings = np.random.randint(1, MAX_RATINGS_PER_NEW_USER + 1)

        # Selecionar itens aleatórios (garantindo que não sejam repetidos)
        item_ids = np.random.choice(
            range(MIN_ITEM_ID, MAX_ITEM_ID + 1), size=num_ratings, replace=False
        )

        # Gerar notas aleatórias (de 1 a 5)
        ratings = np.random.randint(1, 6, size=num_ratings)

        for item_id, rating in zip(item_ids, ratings):
            new_ratings.append(
                {"user_id": user_id, "item_id": item_id, "rating": rating}
            )

    # 4. Concatenar e salvar
    if new_ratings:
        new_df = pd.DataFrame(new_ratings)
        ratings_df = pd.concat([ratings_df, new_df], ignore_index=True)

    # Garantir que a quantidade de linhas seja próxima de TARGET_ROWS
    # (O código acima já faz isso, mas podemos truncar ou adicionar se for preciso)

    ratings_df.to_csv(RATINGS_FILE, index=False)
    print("---")
    print(f"Dataset expandido com sucesso!")
    print(f"Total final de linhas no ratings.csv: {len(ratings_df)}")
    print(f"Novos usuários gerados: {NEW_USERS_TO_ADD}")


if __name__ == "__main__":
    expand_ratings_dataset()

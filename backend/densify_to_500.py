import pandas as pd
import os

# Definição dos caminhos dos arquivos
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
RATINGS_FILE = os.path.join(DATA_DIR, "ratings.csv")
NEW_RATINGS_FILE = os.path.join(DATA_DIR, "new_ratings_dense.csv")

# --- Parâmetros de Poda ---
TARGET_USERS = 500  # Manter os 500 usuários mais ativos


def densify_user_base():
    """Filtra o ratings.csv para manter apenas os usuários mais ativos."""
    try:
        ratings_df = pd.read_csv(RATINGS_FILE)

        print(f"Linhas iniciais: {len(ratings_df)}")
        print(f"Usuários iniciais: {ratings_df['user_id'].nunique()}")

        # 1. Contar as avaliações por usuário
        user_counts = ratings_df["user_id"].value_counts()

        # 2. Selecionar os N usuários mais ativos
        most_active_users = user_counts.nlargest(TARGET_USERS).index.tolist()

        # 3. Filtrar o DataFrame
        new_ratings_df = ratings_df[
            ratings_df["user_id"].isin(most_active_users)
        ].copy()

        # 4. Salvar o novo arquivo
        new_ratings_df.to_csv(NEW_RATINGS_FILE, index=False)

        # Análise do Resultado
        avg_ratings = len(new_ratings_df) / TARGET_USERS
        print("-" * 40)
        print("BASE DE USUÁRIOS DENSIDICADA COM SUCESSO!")
        print(f"Total de Linhas no novo ratings.csv: {len(new_ratings_df)}")
        print(f"Total de Usuários (Target): {TARGET_USERS}")
        print(f"Média de Ratings por Usuário: {avg_ratings:.2f} (Antes: 9.3)")
        print(f"Novo arquivo salvo como: '{NEW_RATINGS_FILE}'")
        print("-" * 40)

    except Exception as e:
        print(f"Erro ao processar os dados: {e}")


if __name__ == "__main__":
    densify_user_base()

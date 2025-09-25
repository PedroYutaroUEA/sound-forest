# Função para carregar o dataset CSV
def load_data():
    try:
        data = pd.read_csv("dataset.csv")
        if (
            "Username" not in data.columns
            or "Game" not in data.columns
            or "Rating" not in data.columns
        ):
            st.error(
                "O arquivo CSV deve conter as colunas: 'Username', 'Game', e 'Rating'."
            )
            return pd.DataFrame(columns=["Username", "Game", "Rating"])
        return data
    except FileNotFoundError:
        st.warning("Arquivo CSV não encontrado. Criando um novo arquivo.")
        return pd.DataFrame(columns=["Username", "Game", "Rating"])


# Função para salvar o dataset atualizado no CSV
def save_data(data):
    data.to_csv("dataset.csv", index=False)


# Função para calcular a similaridade de Pearson
def pearson(rating1, rating2):
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
    denominator = sqrt(sum_x2 - pow(sum_x, 2) / n) * sqrt(sum_y2 - pow(sum_y, 2) / n)
    if denominator == 0:
        return 0
    else:
        return (sum_xy - (sum_x * sum_y) / n) / denominator


# Função para encontrar os vizinhos mais próximos
def computeNearestNeighbor(username, users_ratings):
    distances = []
    current_user_ratings = (
        users_ratings[users_ratings["Username"] == username]
        .set_index("Game")["Rating"]
        .to_dict()
    )
    for user in users_ratings["Username"].unique():
        if user != username:
            other_user_ratings = (
                users_ratings[users_ratings["Username"] == user]
                .set_index("Game")["Rating"]
                .to_dict()
            )
            distance = pearson(current_user_ratings, other_user_ratings)
            distances.append((distance, user))
    distances.sort(reverse=True)
    return distances


# Função com kNN ponderado por similaridade
def recommend(username, users_ratings, game_target=None, k=3):
    neighbors = computeNearestNeighbor(username, users_ratings)
    if not neighbors:
        st.write(f"Nenhum vizinho encontrado para o usuário {username}.")
        return []

    top_neighbors = neighbors[:k]
    total_similarity = sum(sim for sim, _ in top_neighbors)
    if total_similarity == 0:
        st.write("Similaridade total é zero. Não é possível gerar recomendações.")
        return []

    influences = {}  # Cria um dicionário vazio

    # Itera sobre cada vizinho e sua similaridade
    for sim, user in top_neighbors:
        influencia_normalizada = sim / total_similarity  # Calcula o peso proporcional
        influences[user] = influencia_normalizada  # Adiciona ao dicionário

    # Obter os jogos avaliados pelo usuário alvo (por exemplo, “Anny”):
    # Filtra o DataFrame para pegar apenas as avaliações do username escolhido.
    # Usa a coluna "Game" como chave (índice) e pega a coluna "Rating".
    user_ratings = (
        users_ratings[users_ratings["Username"] == username]
        .set_index("Game")["Rating"]
        .to_dict()
    )
    # Inicializa o dicionário onde serão acumuladas as notas previstas
    game_scores = {}

    # Itera sobre os k vizinhos mais próximos:
    # sim: similaridade entre o vizinho e o usuário-alvo
    # neighbor: nome do vizinho.
    for sim, neighbor in top_neighbors:
        # Pega os jogos que o vizinho avaliou:
        neighbor_ratings = (
            users_ratings[users_ratings["Username"] == neighbor]
            .set_index("Game")["Rating"]
            .to_dict()
        )
        # Para cada jogo que o vizinho avaliou, verificar se o usuário-alvo ainda não avaliou:
        for game, rating in neighbor_ratings.items():
            # Ignora jogos que o usuário já avaliou.
            # Ignora entradas com "" (vazias).
            if game not in user_ratings and game != "":
                # Soma a contribuição ponderada pela influência do vizinho:
                # Se o jogo ainda não está em game_scores, inicializa com 0.
                if game not in game_scores:
                    game_scores[game] = 0
                # Adiciona a nota do vizinho multiplicada por sua influência normalizada.
                game_scores[game] += influences[neighbor] * rating

    if not game_scores:
        st.write("Nenhuma recomendação disponível com base nos vizinhos.")
        return []
    # (opcional) o nome de um jogo específico para o qual queremos prever a nota.
    if game_target:
        if game_target in game_scores:
            st.write(
                f"Nota projetada para {username} no jogo '{game_target}': {game_scores[game_target]:.3f}"
            )
        else:
            st.write(
                f"Não há dados suficientes dos vizinhos para projetar nota para '{game_target}'."
            )

    return sorted(game_scores.items(), key=lambda x: x[1], reverse=True)


# Aplicativo Streamlit
def recommend_app():
    st.title("Sistema de Recomendação Colaborativo (kNN Ponderado)")

    if st.button("Go to homne"):
        st.switch_page("pages/home.py")  # Replace with your actual page name

    # users_ratings = load_data()

    # if not users_ratings.empty:
    #     username = st.selectbox(
    #         "Selecione o nome de usuário:", users_ratings["Username"].unique()
    #     )
    #     game_to_rate = st.selectbox(
    #         "Selecione um jogo para avaliar:", users_ratings["Game"].unique()
    #     )
    #     rating = st.slider("Avaliação (1-5):", 1, 5)

    #     # Slider para escolher k (número de vizinhos)
    #     k_value = st.slider("Número de vizinhos mais próximos (k):", 1, 10, 3)

    #     if st.button("Avaliar Jogo"):
    #         new_rating = pd.DataFrame(
    #             {"Username": [username], "Game": [game_to_rate], "Rating": [rating]}
    #         )
    #         users_ratings = pd.concat([users_ratings, new_rating], ignore_index=True)
    #         save_data(users_ratings)
    #         st.write(f"Avaliação para {game_to_rate} adicionada com sucesso!")

    #     if st.button("Recomendar Jogos"):
    #         st.write(
    #             f"Gerando recomendações para {username} usando kNN com influência ponderada..."
    #         )
    #         recommendations = recommend(username, users_ratings, k=k_value)
    #         if recommendations:
    #             st.write("Top recomendações:")
    #             for game, score in recommendations:
    #                 st.write(f"{game} — Nota estimada: {score:.3f}")
    #         else:
    #             st.write("Nenhuma recomendação disponível.")

    # new_user = st.text_input("Digite o nome de um novo usuário:")
    # if st.button("Adicionar Novo Usuário"):
    #     if new_user not in users_ratings["Username"].unique():
    #         users_ratings = pd.concat(
    #             [
    #                 users_ratings,
    #                 pd.DataFrame(
    #                     {"Username": [new_user], "Game": [""], "Rating": [""]}
    #                 ),
    #             ],
    #             ignore_index=True,
    #         )
    #         save_data(users_ratings)
    #         st.write(
    #             f"Novo usuário {new_user} adicionado com sucesso! Recarregue a página para vê-lo na lista."
    #         )
    #     else:
    #         st.write(f"O usuário {new_user} já existe!")

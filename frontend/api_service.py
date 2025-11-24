import requests
import streamlit as st

# Mantenha a URL base configurável
BASE_URL = "http://127.0.0.1:8000"


@st.cache_data(ttl=3600)
def fetch_genres(base_url):
    """Busca a lista de gêneros (função pura e cacheada)."""
    try:
        # Usa o base_url como argumento cacheável
        response = requests.get(f"{base_url}/genres", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar gêneros: {e}")
        return []


class AppService:
    """Gerencia a comunicação com o Backend e o estado da fila de feedback."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Inicializa as variáveis de estado do Streamlit."""
        if "user_id" not in st.session_state:
            st.session_state.user_id = None
        if "recommendations" not in st.session_state:
            st.session_state.recommendations = []
        if "feedback_queue" not in st.session_state:
            st.session_state.feedback_queue = {}
        if "genres_loaded" not in st.session_state:
            st.session_state.genres_loaded = fetch_genres(BASE_URL)

    # --- Funções HTTP (Core Logic) ---

    def simulate_user_api(self, genres):
        try:
            response = requests.post(
                f"{self.base_url}/simulate", json={"genres": genres}, timeout=60
            )
            response.raise_for_status()
            return response.json().get("user_id")
        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao simular usuário: {e}")
            return None

    def fetch_recommendations(self, user_id, n, metric: str = None):
        """Busca recomendações, incluindo o parâmetro 'metric'."""
        params = {"user_id": user_id, "n": n}
        if metric:
            params["metric"] = metric

        try:
            response = requests.get(
                f"{self.base_url}/recomendar", params=params, timeout=60
            )
            response.raise_for_status()
            return response.json().get("recommendations", [])
        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao buscar recomendações: {e}")
            return []

    def send_feedback_star(self, user_id, item_id, rating_value):
        """Envia a nota de 1 a 5 para o backend."""
        try:
            response = requests.post(
                f"{self.base_url}/feedback",
                json={"user_id": user_id, "item_id": item_id, "rating": rating_value},
                timeout=60,
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao enviar avaliação: {e}")
            return False

    # --- Funções de Lógica de Sessão (Transferidas) ---

    def handle_feedback_star(self, item_id, rating):
        """Adiciona o feedback à fila de likes da sessão."""
        st.session_state.feedback_queue[item_id] = rating
        st.info(f"Avaliação de {rating} estrelas registrada na fila.")

    def process_feedback_and_recommend(self, user_id, n, metric: str = None):
        """Processa a fila, envia ao backend e gera novas recomendações."""
        if not st.session_state.feedback_queue:
            st.warning("Nenhum feedback pendente.")
            return

        success_count = 0
        with st.spinner("Processando avaliações e recalculando..."):
            for item_id, rating_value in st.session_state.feedback_queue.items():
                if self.send_feedback_star(user_id, item_id, rating_value):
                    success_count += 1

            st.session_state.feedback_queue = {}
            st.session_state.recommendations = self.fetch_recommendations(
                user_id, n, metric
            )
            st.success(
                f"{success_count} feedbacks processados. Novas recomendações prontas!"
            )
            st.rerun()

    def clear_session(self):
        """Limpa todo o estado da sessão."""
        st.session_state.user_id = None
        st.session_state.recommendations = []
        st.session_state.feedback_queue = {}
        st.rerun()

# frontend/pages/1_Simulacao_e_Recomendacao.py (Código Otimizado)

import streamlit as st
import requests
import os
import json
import pandas as pd  # Adicionado para exibir o DataFrame de itens se necessário
from PIL import Image

# --- Configurações Iniciais ---
BASE_URL = "http://127.0.0.1:8000"

logo_path = "S_UNDFOREST-removebg-preview.png"  # Caminho do arquivo salvo no diretório 'frontend/pages'

# Exibe a imagem centralizada
st.image(logo_path, use_container_width=False, width=500)

# --- Funções de Comunicação (Mantidas) ---


@st.cache_data(ttl=3600)
def fetch_genres():
    # ... (mesmo código de busca de gêneros) ...
    try:
        response = requests.get(f"{BASE_URL}/genres")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar gêneros: {e}")
        return []


def simulate_user_api(genres):
    # ... (mesmo código de simulação de usuário) ...
    try:
        response = requests.post(f"{BASE_URL}/simulate", json={"genres": genres})
        response.raise_for_status()
        return response.json().get("user_id")
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao simular usuário: {e}")
        return None


def fetch_recommendations(user_id, n=20):
    # ... (mesmo código de busca de recomendações) ...
    try:
        response = requests.get(f"{BASE_URL}/recomendar?user_id={user_id}&n={n}")
        response.raise_for_status()
        return response.json().get("recommendations", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar recomendações: {e}")
        return []


# --- Funções de Lógica (Novo) ---


def handle_like(item_id, like=True):
    """Adiciona o feedback à fila de likes da sessão."""
    if item_id not in st.session_state.feedback_queue:
        st.session_state.feedback_queue[item_id] = like
    else:
        # Permite mudar de opinião (like/dislike)
        st.session_state.feedback_queue[item_id] = like
    st.info(
        f"Feedback para **{item_id}** registrado na fila. Pressione o botão para gerar novas recomendações."
    )


def send_feedback_star(user_id, item_id, rating_value):
    """Envia a nota de 1 a 5 para o backend."""
    try:
        response = requests.post(
            f"{BASE_URL}/feedback",
            json={
                "user_id": user_id,
                "item_id": item_id,
                # Note que a chave "like" é substituída por "rating_value"
                # Precisamos ajustar o backend para receber o rating diretamente!
                "rating": rating_value,
            },
            timeout=60,
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao enviar avaliação: {e}")
        return False


def process_feedback_and_recommend(user_id):
    """Processa todos os likes na fila e gera novas recomendações."""
    if not st.session_state.feedback_queue:
        st.warning("Nenhum novo like ou dislike para processar.")
        return

    success_count = 0
    with st.spinner("Processando avaliações e recalculando recomendações..."):
        for (
            item_id,
            rating_value,
        ) in (
            st.session_state.feedback_queue.items()
        ):  # Itera sobre o valor da estrela (1 a 5)
            # CHAMA NOVA FUNÇÃO DE ENVIO COM A NOTA
            if send_feedback_star(user_id, item_id, rating_value):
                success_count += 1

        # Limpa a fila após o processamento
        st.session_state.feedback_queue = {}

        # Gera a nova recomendação
        st.session_state.recommendations = fetch_recommendations(user_id)

        st.success(
            f"{success_count} feedbacks processados. Novas recomendações prontas!"
        )


# --- Gerenciamento de Sessão ---
# Adiciona o novo estado para a fila de feedbacks
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "feedback_queue" not in st.session_state:
    st.session_state.feedback_queue = {}
if "genres_loaded" not in st.session_state:
    st.session_state.genres_loaded = fetch_genres()


# --- Layout ---

# Correção na Simulação Inicial: Garantir que sempre há um ID de usuário
if st.session_state.user_id is None:
    st.header("1. Simulação Inicial do Usuário")
    st.info(
        "O sistema criará um novo ID de usuário com base nos seus gostos iniciais e gerará a primeira lista de músicas."
    )

    selected_genres = st.multiselect(
        "Selecione seus gêneros musicais de interesse:",
        options=st.session_state.genres_loaded,
        default=(
            st.session_state.genres_loaded[:3] if st.session_state.genres_loaded else []
        ),
    )

    if st.button("Simular e Gerar Primeira Recomendação"):
        if selected_genres:
            with st.spinner("Criando perfil e gerando recomendações..."):
                new_user_id = simulate_user_api(selected_genres)
                if new_user_id is not None:
                    st.session_state.user_id = new_user_id
                    st.session_state.recommendations = fetch_recommendations(
                        new_user_id
                    )
                    st.success(f"Usuário simulado com sucesso (ID: {new_user_id}).")
                    st.rerun()
        else:
            st.warning("Por favor, selecione pelo menos um gênero.")

# --- NOVA FUNÇÃO DE HANDLE FEEDBACK NO FRONTEND ---


def handle_feedback_star(item_id, rating):
    """Adiciona o feedback (estrela) à fila de likes da sessão."""
    st.session_state.feedback_queue[item_id] = rating  # Armazena o valor (1 a 5)
    st.info(f"Avaliação de {rating} estrelas para **{item_id}** registrada na fila.")


# --- Seção de Recomendações Contínuas ---
if st.session_state.user_id is not None:
    current_user = st.session_state.user_id
    st.sidebar.success(f"Perfil Ativo: Usuário ID **{current_user}**")

    st.header(f"2. Suas Recomendações")

    # NOVO: Botão principal para processar likes e gerar novas recomendações
    if st.button("✨ Gerar Novas Recomendações (Processar Likes)", type="primary"):
        process_feedback_and_recommend(current_user)

    if st.session_state.feedback_queue:
        st.warning(
            f"Você tem **{len(st.session_state.feedback_queue)}** feedbacks pendentes. Clique no botão acima!"
        )

if st.session_state.recommendations:
    st.write("### Recomendações Atuais")

    cols_per_row = 5
    recs = st.session_state.recommendations

    for row_start in range(0, len(recs), cols_per_row):
        cols = st.columns(cols_per_row)
        for col, rec in zip(cols, recs[row_start : row_start + cols_per_row]):
            with col:
                st.markdown(
                    f"""
                    <div style='
                        width:140px;
                        height:140px;
                        padding:8px;
                        margin:5px auto;
                        border-radius:8px;
                        background-color:#f0f0f0;
                        border:1px solid #ccc;
                        display:flex;
                        flex-direction:column;
                        justify-content:center;
                        align-items:center;
                        text-align:center;
                        overflow:hidden;
                    '>
                        <div style='font-weight:bold; color:#000; font-size:12px;
                                    white-space:nowrap; overflow:hidden; text-overflow:ellipsis; width:120px;'>
                            {rec['title']}
                        </div>
                        <div style='color:#333; font-size:11px; margin-top:2px;
                                    white-space:nowrap; overflow:hidden; text-overflow:ellipsis; width:120px;'>
                            {rec['artist']}
                        </div>
                        <div style='color:#0066cc; font-size:11px; margin-top:2px;'>
                            {rec['genre']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Slider compacto
                rating_value = st.slider(
                    "⭐",
                    min_value=1,
                    max_value=5,
                    value=3,
                    key=f"slider_{rec['item_id']}",
                    label_visibility="collapsed",
                )

                if st.button("OK", key=f"submit_{rec['item_id']}"):
                    handle_feedback_star(rec["item_id"], rating_value)
                    st.rerun()

    else:
        st.warning("Nenhuma recomendação disponível. Tente selecionar mais gêneros.")

# --- Botão de Limpeza de Sessão ---
st.sidebar.divider()
if st.sidebar.button("Limpar Sessão e Voltar ao Início"):
    st.session_state.user_id = None
    st.session_state.recommendations = []
    st.session_state.feedback_queue = {}
    st.rerun()

# botao pra pagina de acuracia
if st.button("Ir para Análise de Acurácia"):
    st.switch_page("pages/2_Analise_Acuracia.py")

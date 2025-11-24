import streamlit as st
from api_service import AppService

# -------------------------------------------------------------
# CORREÇÃO: INJEÇÃO DE TEMA (Mantido para o visual)
# ... (Insira o bloco de injeção de CSS Marrom/Verde aqui) ...
# -------------------------------------------------------------
# Cores do tema (Marrom Escuro e Verde Floresta)
BACKGROUND_COLOR = "#a2a29d"
HEADER_COLOR = "#e8e8e8"
ASIDE = "#828693"
TEXT_COLOR = "#050608"
ASIDE_BUTTON_HOVER = "#495464"
ASIDE_BUTTON_COLOR = "#495464AC"
PRIMARY_COLOR = "#38761d"
SECONDARY_BACKGROUND = "#4d2800"

st.markdown(
    f"""
    <style>
    /* ---------------------- CORES GERAIS ESTÁVEIS ---------------------- */
    .stApp {{ background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR}; }}
    [data-testid="stSidebar"] {{ background-color: {ASIDE}; }}
    .stAppToolbar {{ background-color: {HEADER_COLOR}; }}
    
    /* Títulos e texto principal */
    h1, h2, h3, h4, .stMarkdown, .stText {{ color: {TEXT_COLOR} !important; }}
    
    /* ---------------------- CORES DE INTERAÇÃO (VERDE) ---------------------- */
    /* Cor dos botões (Verde Floresta) */
    .stButton>button {{
        background-color: {PRIMARY_COLOR} !important;
        border-color: {PRIMARY_COLOR} !important;
        color: white !important;
    }}
    
    /* Cor da barra de progresso do slider (Verde Floresta) */
    .stSlider > div > div:nth-child(2) > div:nth-child(1) {{
        background-color: {PRIMARY_COLOR};
    }}

    [data-testid="stSidebarNavLink"] {{
        background-color: {ASIDE_BUTTON_COLOR};
    }}
    [data-testid="stSidebarNavLink"]:hover {{
        background-color: {ASIDE_BUTTON_HOVER};
    }}

    /* ---------------------- CORES DE INPUTS (Cinza/Preto) ---------------------- */

    /* CORREÇÃO 1: Fundo do Selectbox (Onde a opção selecionada aparece - Deve ser Cinza) */
    /* Este seletor atinge a caixa de entrada (navbar-style) */
    [data-testid="stSelectbox"] div[data-testid="stForm"] > div, 
    [data-testid="stSelectbox"] div[role="button"] {{
        background-color: {ASIDE}; /* Cinza da sidebar/navbar */
        color: {TEXT_COLOR} !important; /* Texto preto/escuro no seletor */
        border-color: {ASIDE};
    }}
    
    /* CORREÇÃO 2: Rótulos do Slider e do Selectbox (Texto Preto) */
    /* Seleciona o rótulo (texto "Escolha a Métrica...") */
    label.css-1nwvave {{
        color: {TEXT_COLOR} !important; /* Preto */
    }}
    
    /* CORREÇÃO 3: Fonte do Slider (Os números ao lado da barra) */
    .stSlider > div > div:nth-child(2) > div:nth-child(2) > div {{
        color: {TEXT_COLOR} !important; /* Preto */
        background-color: transparent !important;
    }}
    
    </style>
    """,
    unsafe_allow_html=True,
)
# Inicializa o serviço e o estado de sessão
service = AppService()

# --- Configurações Visuais ---
LOGO_PATH = "S_UNDFOREST-removebg-preview.png"

# Centraliza a imagem (usando HTML/CSS para garantir)
st.markdown(
    "<div style='display:flex; justify-content:center;'>", unsafe_allow_html=True
)


st.image(LOGO_PATH, use_container_width=False, width=500)
st.markdown("</div>", unsafe_allow_html=True)

# --- Controles de Configuração e Parâmetro Metric ---
st.sidebar.header("⚙️ Configurações do Algoritmo")

# 1. Parâmetro Metric
metric_options = {
    "Similaridade de Cossenos": "cosine",
    "Correlação de Pearson": "pearson",
}
selected_metric_name = st.sidebar.selectbox(
    "Métrica de Similaridade:", options=list(metric_options.keys()), index=0
)
selected_metric = metric_options[selected_metric_name]
st.sidebar.info(f"O sistema usará: **{selected_metric_name}**.")

# 2. Número de Recomendações
N_RECOMMEND = st.sidebar.slider(
    "Número de Músicas (N)", min_value=5, max_value=30, value=20
)

# --- 1. Simulação Inicial ---

if st.session_state.user_id is None:
    st.header("1. Simulação Inicial do Usuário")
    # ... (restante da UI de simulação) ...

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
                new_user_id = service.simulate_user_api(selected_genres)
                if new_user_id is not None:
                    st.session_state.user_id = new_user_id
                    st.session_state.recommendations = service.fetch_recommendations(
                        new_user_id, N_RECOMMEND, selected_metric
                    )
                    st.success(f"Usuário simulado com sucesso (ID: {new_user_id}).")
                    st.rerun()
        else:
            st.warning("Por favor, selecione pelo menos um gênero.")


# --- 2. Seção de Recomendações Contínuas ---

if st.session_state.user_id is not None:
    current_user = st.session_state.user_id
    st.sidebar.success(f"Perfil Ativo: Usuário ID **{current_user}**")

    st.header("2. Suas Recomendações")

    # Botão principal para processar likes e gerar novas recomendações
    if st.button("✨ Gerar Novas Recomendações (Processar Likes)", type="primary"):
        service.process_feedback_and_recommend(
            current_user, N_RECOMMEND, selected_metric
        )

    if st.session_state.feedback_queue:
        st.warning(
            f"Você tem **{len(st.session_state.feedback_queue)}** feedbacks pendentes. Clique no botão acima!"
        )

    if st.session_state.recommendations:
        st.write(f"### Recomendações Atuais (Usando {selected_metric_name})")

        COLS_PER_ROW = 5
        recs = st.session_state.recommendations

        for row_start in range(0, len(recs), COLS_PER_ROW):
            cols = st.columns(COLS_PER_ROW)
            for col, rec in zip(cols, recs[row_start : row_start + COLS_PER_ROW]):
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

                    rating_value = st.slider(
                        "⭐",
                        min_value=1,
                        max_value=5,
                        value=3,
                        key=f"slider_{rec['item_id']}",
                        label_visibility="collapsed",
                    )

                    if st.button("OK", key=f"submit_{rec['item_id']}"):
                        service.handle_feedback_star(rec["item_id"], rating_value)
                        st.rerun()
    else:
        st.warning("Nenhuma recomendação disponível.")

# --- Botão de Limpeza e Navegação ---
st.sidebar.divider()
if st.sidebar.button("Limpar Sessão e Voltar ao Início"):
    service.clear_session()

# Botão de navegação (corrigido)
if st.button("Ir para Análise de Acurácia"):
    st.switch_page("pages/2_Avaliacao_Acuracia.py")

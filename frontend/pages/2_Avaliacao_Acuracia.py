import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

BACKGROUND_COLOR = "#696969"
HEADER_COLOR = "#e8e8e8"
ASIDE = "#828693"
TEXT_COLOR = "#050608"
ASIDE_BUTTON_HOVER = "#495464"
ASIDE_BUTTON_COLOR = "#495464AC"
PRIMARY_COLOR = "#38761d"
SECONDARY_BACKGROUND = "#4d2800"

st.set_page_config(
    page_title="SOUNDFOREST - Acurácia",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
    <style>
    /* ---------------------- CORES DE FUNDO GERAIS ---------------------- */
    .stApp {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
    }}
    [data-testid="stSidebar"] {{
        background-color: {ASIDE};
    }}
    [data-testid="stSidebarNavItems"] * {{
        color: {HEADER_COLOR};
        font-weight: bold;
    }}
    [data-testid="stSidebarNavLink"] {{
        background-color: {ASIDE_BUTTON_COLOR};
    }}
    [data-testid="stSidebarNavLink"]:hover {{
        background-color: {ASIDE_BUTTON_HOVER};
    }}
    /* Cor dos botões e sliders (Verde Floresta) */
    .stButton>button {{
        background-color: {PRIMARY_COLOR} !important;
        border-color: {PRIMARY_COLOR} !important;
        color: white !important;
    }}
    /*app header*/
    .stAppToolbar {{
      background-color: {HEADER_COLOR};
    }}
    /* Fundo dos widgets de entrada */
    [data-testid="stForm"], 
    [data-testid^="stWidget"] > div {{
        color: {TEXT_COLOR};
    }}
    /* Títulos e texto principal */
    h1, h2, h3, h4, .stMarkdown, .stText {{
        color: {TEXT_COLOR} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_URL = "http://127.0.0.1:8000"

st.title("📊 Análise de Acurácia do Sistema")

st.markdown(
    """
    Nesta tela você pode calcular a **acurácia** das recomendações:
    
    - Divide as avaliações em **treino (70%)** e **teste (30%)**.
    - O sistema recomenda músicas com base no treino.
    - Verifica quantas do **teste** apareceram nas recomendações.
    
    Fórmula:
    `Acurácia = nº de acertos / nº de recomendações`
    """
)


# ---------------------------
# Utilitário para conversão
# ---------------------------
def convert(obj):
    if isinstance(obj, dict):
        return {k: convert(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert(v) for v in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    else:
        return obj


# ---------------------------
# Opções de entrada
# ---------------------------
metric_options = {"Cossenos": "cosine", "Pearson": "pearson"}
selected_metric_name = st.selectbox(
    "Escolha a Métrica de Similaridade:",
    options=list(metric_options.keys()),
    index=0,  # Cossenos é a opção default
)
selected_metric = metric_options[selected_metric_name]
st.info(f"O algoritmo de Filtragem Colaborativa usará: **{selected_metric_name}**.")

st.markdown("---")

mode = st.radio("Escolha o modo:", ["Média (todos usuários)", "Usuário específico"])

if mode == "Média (todos usuários)":
    max_users = st.slider("Limite de usuários a avaliar:", 5, 100, 20, step=5)
else:
    max_users = None

if mode == "Usuário específico":
    user_id = st.number_input("ID do usuário:", min_value=1, step=1)
else:
    user_id = None

n_recommend = st.slider("Nº de recomendações a testar:", 5, 50, 10, step=5)
test_frac = st.slider("Proporção de teste:", 0.1, 0.9, 0.3, step=0.1)

# ---------------------------
# Botão principal
# ---------------------------
if st.button("Calcular Acurácia"):
    try:
        params = {
            "n_recommend": n_recommend,
            "test_frac": test_frac,
            "metric": selected_metric,
        }
        if max_users:
            params["max_users"] = max_users
        if user_id is not None and mode == "Usuário específico":
            params["user_id"] = int(user_id)

        # Chamada à API
        response = requests.get(f"{BASE_URL}/accuracy", params=params, timeout=120)
        response.raise_for_status()
        result = convert(response.json())

        st.success("✅ Resultado obtido com sucesso!")

        # Exibir resultados crus
        full_result = result.copy()
        full_result["test_proportion"] = test_frac
        st.json(full_result)

        # Caso 1: Acurácia média
        if "mean_accuracy" in result:
            st.metric("Acurácia Média", f"{result['mean_accuracy']*100:.2f}%")
            st.write(
                f"Usuários avaliados: {result['n_users_evaluated']} (limite {result.get('max_users', 'N/A')})"
            )

            #  Gráfico de acurácia por usuário (se backend retornar lista detalhada)
            if "user_accuracies" in result:
                df = pd.DataFrame(result["user_accuracies"])
                fig, ax = plt.subplots()
                df.plot(kind="bar", x="user_id", y="accuracy", legend=False, ax=ax)
                ax.set_ylabel("Acurácia")
                ax.set_xlabel("Usuário")
                ax.set_title("Acurácia por Usuário")
                st.pyplot(fig)

        # Caso 2: Usuário específico
        elif "accuracy" in result:
            st.metric("Acurácia", f"{result['accuracy']*100:.2f}%")
            st.write(f"Usuário: {result['user_id']}")
            st.write(
                f"Acertos: {result['hits']} em {result['recommended']} recomendações"
            )

    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao calcular acurácia: {e}")

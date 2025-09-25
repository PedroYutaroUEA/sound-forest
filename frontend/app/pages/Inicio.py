import os
import streamlit as st
import requests
from app.config import Config


def query_initial_recommendation(generos_selecionados) -> bool:
    with st.spinner("Gerando recomendações..."):
        try:
            api_url = Config.API_URL
            endpoint = f"{api_url}/api/initial-recommend"
            data = {"genres": generos_selecionados}
            response = requests.post(endpoint, json=data, timeout=50)

            if response.status_code == 200:
                recomendacoes = response.json()
                st.session_state.recomendacoes_iniciais = recomendacoes
                st.success("Recomendações geradas com sucesso!")
                # Oculta o formulário de gêneros e mostra o resultado
                st.rerun()
                return True
            else:
                st.error(f"Erro ao conectar com o backend: {response.text}")
                return False
        except requests.exceptions.ConnectionError as e:
            st.error(
                f"Erro de conexão: Verifique se o backend está rodando em {backend_url}"
            )


# Exibe as recomendações da sessão se existirem
def INITIAL_RECOMMENDATIONS_LIST():
    if (
        "recomendacoes_iniciais" in st.session_state
        and st.session_state.recomendacoes_iniciais
    ):
        st.subheader("Instrumentos Recomendados para Você:")
        for item in st.session_state.recomendacoes_iniciais:
            st.write(f"- {item['nome']} ({item['genero_principal']})")
            # Botão de like
            if st.button(f"Gostei de {item['nome']}", key=f"like_{item['item_id']}"):
                # Lógica para enviar o like para o backend (usando o endpoint de filtragem colaborativa)
                st.session_state.liked_item_id = item["item_id"]
                st.success(
                    f"Você curtiu {item['nome']}! Vamos adaptar suas recomendações."
                )
                st.info(
                    "Por favor, navegue para a página 'Recomendar' para ver novas recomendações!"
                )


def INITIAL_RECOMMENDATIONS_STARTER():
    st.title("Recomendação Inicial")
    generos = [
        "Rock",
        "MPB",
        "Jazz",
        "Clássica",
        "Samba",
        "Blues",
        "Eletrônica",
        "Forró",
        "Folk",
    ]
    generos_selecionados = st.multiselect(
        "Quais estilos musicais você gosta?",
        options=generos,
        placeholder="Selecione seus gêneros favoritos",
    )

    if st.button("Gerar Recomendações"):
        if not generos_selecionados:
            st.warning("Por favor, selecione pelo menos um gênero musical.")
        else:
            if query_initial_recommendation(generos_selecionados):
                INITIAL_RECOMMENDATIONS_LIST()


if __name__ == "__main__":
    INITIAL_RECOMMENDATIONS_STARTER()

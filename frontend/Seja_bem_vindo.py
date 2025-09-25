import streamlit as st
import pandas as pd
from math import sqrt, pow


def app():
    st.set_page_config(
        page_title="Sound Forest",
        page_icon="🎵",
    )

    st.title("Descubra o Instrumento Perfeito")
    st.sidebar.success("Selecione uma página acima.")

    st.markdown(
        """
        Seja bem-vindo ao sistema de recomendação de instrumentos musicais!
        Para começar, use a barra lateral para ir à página **Recomendação Inicial**.
        """
    )


if __name__ == "__main__":
    app()

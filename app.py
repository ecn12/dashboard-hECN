import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dashboard Hidrológico",
    layout="wide"
)

st.title("Dashboard Hidrológico")

st.markdown("### Monitoramento Hidrológico")

arquivo = st.file_uploader(
    "Upload CSV da estação",
    type=["csv"]
)

if arquivo:

    df = pd.read_csv(
        arquivo,
        sep=";",
        encoding="latin1"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Estações",
            "1"
        )

    with col2:
        st.metric(
            "Registros",
            f"{len(df):,}"
        )

    with col3:
        st.metric(
            "Arquivo",
            "Carregado"
        )

    st.success("CSV carregado com sucesso.")

    st.markdown("---")

    st.button("Abrir Estação Quizanga")

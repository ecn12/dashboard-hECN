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

    df["datetime"] = pd.to_datetime(
        df.iloc[:, 1],
        format="%d/%m/%Y %H:%M"
    )

    ultima_data = df["datetime"].max()

    dias_dados = (
        ultima_data.date()
        -
        df["datetime"].min().date()
    ).days

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Estações",
            "1"
        )

    with col2:
        st.metric(
            "Última Atualização",
            ultima_data.strftime("%d/%m/%Y")
        )

    with col3:
        st.metric(
            "Dias de Dados",
            f"{dias_dados:,}"
        )

    st.success("CSV carregado com sucesso.")

    st.markdown("---")

    col_mapa, col_card = st.columns([2, 1])

    with col_mapa:

        mapa = pd.DataFrame({
            "lat": [-22.520277],
            "lon": [-42.830555]
        })

        st.subheader("Localização da Estação")

        st.map(mapa)

    with col_card:

        st.subheader("Quizanga")

        st.metric(
            "Nível Atual",
            "1,37 m"
        )

        st.metric(
            "Variação (7 dias)",
            "-0,20 m"
        )

        st.metric(
            "Tendência",
            "↓ Decrescente"
        )

    st.markdown("---")

    st.button("Abrir Estação Quizanga")

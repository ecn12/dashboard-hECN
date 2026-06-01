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

    # =========================
    # LEITURA DO CSV
    # =========================

    df = pd.read_csv(
        arquivo,
        sep=";",
        encoding="latin1"
    )

    # Coluna de data
    df["datetime"] = pd.to_datetime(
        df.iloc[:, 1],
        format="%d/%m/%Y %H:%M",
        errors="coerce"
    )

    # Coluna de nível
    df["nivel"] = pd.to_numeric(
        df.iloc[:, 3],
        errors="coerce"
    )

    # Remove linhas inválidas
    df = df.dropna(
        subset=["datetime", "nivel"]
    )

    # Ordena por data
    df = df.sort_values(
        "datetime"
    )

    # =========================
    # INDICADORES
    # =========================

    ultima_data = df["datetime"].max()

    dias_dados = (
        ultima_data.date()
        -
        df["datetime"].min().date()
    ).days

    nivel_atual = df["nivel"].iloc[-1]

    if len(df) >= 8:

        nivel_7dias = df["nivel"].iloc[-8]

        variacao = (
            nivel_atual
            -
            nivel_7dias
        )

    else:

        variacao = 0

    if variacao > 0.05:

        tendencia = "↑ Crescente"

    elif variacao < -0.05:

        tendencia = "↓ Decrescente"

    else:

        tendencia = "→ Estável"

    # =========================
    # CARDS SUPERIORES
    # =========================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Estações",
            "1"
        )

    with col2:

        st.metric(
            "Última Atualização",
            ultima_data.strftime(
                "%d/%m/%Y"
            )
        )

    with col3:

        st.metric(
            "Dias de Dados",
            f"{dias_dados:,}"
        )

    st.success(
        "CSV carregado com sucesso."
    )

    st.markdown("---")

    # =========================
    # MAPA + CARD
    # =========================

    col_mapa, col_card = st.columns(
        [2, 1]
    )

    with col_mapa:

        st.subheader(
            "Localização da Estação"
        )

        mapa = pd.DataFrame(
            {
                "lat": [-22.520277],
                "lon": [-42.830555]
            }
        )

        st.map(mapa)

    with col_card:

        st.subheader("Quizanga")

        st.metric(
            "Nível Atual",
            f"{nivel_atual:.2f} m"
        )

        st.metric(
            "Última Atualização",
            ultima_data.strftime(
                "%d/%m/%Y"
            )
        )

        st.metric(
            "Variação (7 dias)",
            f"{variacao:.2f} m"
        )

        st.metric(
            "Tendência",
            tendencia
        )

    st.markdown("---")

    st.button(
        "Abrir Estação Quizanga"
    )

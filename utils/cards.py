
import streamlit as st

def mostrar_card(
    nivel_atual,
    percentil_sazonal,
    percentil_serie,
    variacao_m,
    variacao_pct,
    tendencia
):

    st.metric(
        "Nível Atual",
        f"{nivel_atual:.2f} m"
    )

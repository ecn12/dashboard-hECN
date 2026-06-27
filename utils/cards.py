import streamlit as st

def mostrar_card(
    nivel_atual,
    percentil_sazonal,
    percentil_serie,
    variacao_m,
    variacao_pct,
    tendencia
):

    st.subheader("Situação Atual")

    st.metric(
        "Nível Atual",
        f"{nivel_atual:.2f} m"
    )

    st.metric(
        "Percentil Sazonal",
        f"P{percentil_sazonal}"
    )

    st.metric(
        "Percentil Série",
        f"P{percentil_serie}"
    )

    st.metric(
        "Variação (7 dias)",
        f"{variacao_m:.2f} m",
        delta=f"{variacao_pct:.1f}%"
    )

    st.metric(
        "Tendência",
        tendencia
    )

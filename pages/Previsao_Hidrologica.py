import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.processamento import processar_dados
from utils.cabecalho import mostrar_cabecalho
st.divider()

# ==========================================================
# ÚLTIMOS 7 DIAS OBSERVADOS
# ==========================================================

st.divider()

st.subheader("Nível observado - Últimos 7 dias")

ultima_data = nivel_diario["data"].max()

observado = nivel_diario[
    nivel_diario["data"] >= ultima_data - pd.Timedelta(days=7)
].copy()

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=observado["data"],
        y=observado["nivel"],
        mode="lines+markers",
        name="Observado",
        line=dict(
            color="black",
            width=3
        ),
        marker=dict(size=6)
    )
)

fig.update_layout(
    height=500,
    template="plotly_white",
    xaxis_title="Data",
    yaxis_title="Nível (m)",
    margin=dict(l=20, r=20, t=40, b=20)
)

st.plotly_chart(
    fig,
    use_container_width=True
)

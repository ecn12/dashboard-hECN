import streamlit as st
import pandas as pd

from utils.processamento import processar_dados
from utils.cabecalho import mostrar_cabecalho
st.divider()

st.info(
    "🚧 Módulo de previsão hidrológica em desenvolvimento.\n\n"
    "Nas próximas versões será apresentada a previsão de nível para os próximos 7 dias."
)

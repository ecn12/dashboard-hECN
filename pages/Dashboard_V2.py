import streamlit as st
import pandas as pd

from utils.processamento import processar_dados

st.set_page_config(
    page_title="Dashboard Hidrológico",
    layout="wide"
)

st.title("Dashboard Hidrológico")

# ==========================
# Lê o cadastro das estações
# ==========================

cadastro = pd.read_csv(
    "dados/cadastro_estacoes.csv"
)

# ==========================
# Escolha da estação
# ==========================

estacao = st.selectbox(
    "Selecione a estação",
    cadastro["nome"]
)

# ==========================
# Descobre qual arquivo abrir
# ==========================

arquivo = cadastro.loc[
    cadastro["nome"] == estacao,
    "arquivo"
].iloc[0]

st.success(f"Arquivo selecionado: {arquivo}")

# ==========================
# Lê automaticamente o CSV
# ==========================

df = pd.read_csv(
    f"dados/historico/{arquivo}",
    sep=";",
    encoding="latin1"
)

st.subheader("Primeiras linhas do arquivo")

st.dataframe(df.head())

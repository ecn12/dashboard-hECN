import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.processamento import processar_dados
from utils.indicadores import calcular_indicadores
from utils.cabecalho import mostrar_cabecalho
from utils.graficos_previsao import gerar_grafico_previsao

# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Dashboard Hidrológico",
    layout="wide"
)

# ==========================================================
# LEITURA DO CADASTRO DAS ESTAÇÕES
# ==========================================================

cadastro = pd.read_csv("dados/estacoes.csv")
cadastro["ativo"] = cadastro["ativo"].astype(int)
cadastro = cadastro[cadastro["ativo"] == 1]

# ==========================================================
# SELEÇÃO DA ESTAÇÃO
# ==========================================================

estacao = st.selectbox("Selecione a estação", cadastro["nome"])
dados_estacao = cadastro.loc[cadastro["nome"] == estacao].iloc[0]

arquivo = dados_estacao["arquivo"]
rio = dados_estacao["rio"]
municipio = dados_estacao["municipio"]
estado = dados_estacao["estado"]
redec = dados_estacao["REDEC"]
operador = dados_estacao["operador"]
tipo = dados_estacao["tipo"]

# ==========================================================
# LEITURA DA SÉRIE HISTÓRICA
# ==========================================================

df = pd.read_csv(
    f"dados/historico/{arquivo}",
    sep=";",
    encoding="latin1"
)

# ==========================================================
# PROCESSAMENTO DOS DADOS
# ==========================================================

nome_estacao, P95, nivel_diario, estatisticas = processar_dados(df)

(
    nivel_atual,
    percentil_sazonal,
    percentil_serie,
    variacao_m,
    variacao_pct,
    tendencia
) = calcular_indicadores(nivel_diario)

ultima_atualizacao = nivel_diario["data"].max()

# ==========================================================
# CABEÇALHO
# ==========================================================

mostrar_cabecalho(
    rio,
    estacao,
    operador,
    municipio,
    estado,
    redec,
    tipo,
    ultima_atualizacao
)

# ==========================================================
# GRÁFICO PRINCIPAL
# ==========================================================

st.subheader("Previsão Hidrológica - Próximos 7 dias")

ultima_data = nivel_diario["data"].max()

inicio = ultima_data - pd.Timedelta(days=7)

ultima_data = nivel_diario["data"].max()

observado = nivel_diario[
    (nivel_diario["data"] >= inicio) &
    (nivel_diario["data"] <= ultima_data)
]

df_grafico = observado.merge(
    estatisticas,
    on="mes_dia",
    how="left"
)


ultima_data = nivel_diario["data"].max()

observado = nivel_diario[
    nivel_diario["data"] >= ultima_data - pd.Timedelta(days=7)
].copy()

fig = gerar_grafico_previsao(
    observado,
    estatisticas,
    P95,
    nome_estacao
)

st.plotly_chart(
    fig,
    use_container_width=True
)


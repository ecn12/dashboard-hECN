import streamlit as st
import pandas as pd

from utils.processamento import processar_dados
from utils.indicadores import calcular_indicadores
from utils.graficos import (
    gerar_grafico,
    gerar_grafico_contexto
)

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

nome_estacao, P95, nivel_diario, estatisticas = processar_dados(df)
(
    nivel_atual,
    percentil_sazonal,
    percentil_serie,
    variacao_m,
    variacao_pct,
    tendencia
) = calcular_indicadores(nivel_diario)

# ===========================================
# PERÍODO DO PRIMEIRO GRÁFICO
# ===========================================

periodo = st.radio(
    "Selecione o período",
    ['15 dias', '1 mês', '4 meses', '12 meses', 'Série completa'],
    horizontal=True
)

ultima_data = nivel_diario['data'].max()

if periodo == '15 dias':
    inicio = ultima_data - pd.Timedelta(days=15)

elif periodo == '1 mês':
    inicio = ultima_data - pd.DateOffset(months=1)

elif periodo == '4 meses':
    inicio = ultima_data - pd.DateOffset(months=4)

elif periodo == '12 meses':
    inicio = ultima_data - pd.DateOffset(years=1)

else:
    inicio = nivel_diario['data'].min()


observado = nivel_diario[
    (nivel_diario['data'] >= inicio) &
    (nivel_diario['data'] <= ultima_data)
]

grafico = observado.merge(
    estatisticas,
    on='mes_dia',
    how='left'
)

fig = gerar_grafico(
    grafico,
    nome_estacao,
    periodo,
    P95
)

st.plotly_chart(
    fig,
    use_container_width=True
)

import streamlit as st
import pandas as pd

from utils.processamento import processar_dados
from utils.indicadores import calcular_indicadores
from utils.graficos import (
    gerar_grafico,
    gerar_grafico_contexto
)
from utils.cards import mostrar_card
from utils.cabecalho import mostrar_cabecalho

st.set_page_config(
    page_title="Dashboard Hidrológico",
    layout="wide"
)

# ==========================
# Lê o cadastro das estações
# ==========================

cadastro = pd.read_csv(
    "dados/estacoes.csv"
)

cadastro["ativo"] = cadastro["ativo"].astype(int)

cadastro = cadastro[
    cadastro["ativo"] == 1
]
# ==========================
# Escolha da estação
# ==========================

estacao = st.selectbox(
    "Selecione a estação",
    cadastro["nome"]
)
dados_estacao = cadastro[
    cadastro["nome"] == estacao
].iloc[0]

rio = dados_estacao["rio"]

municipio = dados_estacao["municipio"]

estado = dados_estacao["estado"]

redec = dados_estacao["REDEC"]

operador = dados_estacao["operador"]

tipo = dados_estacao["tipo"]

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

ultima_atualizacao = nivel_diario["data"].max()

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

st.divider()

periodo_contexto = st.radio(
    "Selecione o período do Contexto Hidrológico",
    ['15 dias', '1 mês', '4 meses', '12 meses', 'Série completa'],
    horizontal=True,
    key="contexto"
)
fig_contexto = gerar_grafico_contexto(
    nivel_diario,
    estatisticas,
    P95,
    nome_estacao,
    periodo_contexto
)

st.plotly_chart(
    fig_contexto,
    use_container_width=True
)

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

col_grafico, col_card = st.columns([5.2, 1])

with col_grafico:

    st.plotly_chart(
        fig,
        use_container_width=True
    )

with col_card:

    mostrar_card(
        nivel_atual,
        percentil_sazonal,
        percentil_serie,
        variacao_m,
        variacao_pct,
        tendencia
    )


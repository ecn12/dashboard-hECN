```python
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Dashboard Hidrológico",
    layout="wide"
)

# ============================================================
# PROCESSAMENTO
# ============================================================

def processar_dados(df):

    df.columns = ['estacao', 'datetime', 'chuva', 'nivel']

    df = df.replace(['SD', '9999'], pd.NA)

    df['datetime'] = pd.to_datetime(
        df['datetime'],
        format='%d/%m/%Y %H:%M'
    )

    df['chuva'] = pd.to_numeric(df['chuva'], errors='coerce')
    df['nivel'] = pd.to_numeric(df['nivel'], errors='coerce')

    df.loc[df['nivel'] > 20, 'nivel'] = pd.NA
    df.loc[df['chuva'] > 500, 'chuva'] = pd.NA

    nome_estacao = df['estacao'].dropna().iloc[0]

    P95 = df['nivel'].quantile(0.05)

    df['data'] = df['datetime'].dt.floor('D')

    nivel_diario = df.groupby('data')['nivel'].max()

    datas_completas = pd.date_range(
        start=nivel_diario.index.min(),
        end=nivel_diario.index.max(),
        freq='D'
    )

    nivel_diario = nivel_diario.reindex(datas_completas)

    nivel_diario = nivel_diario.reset_index()
    nivel_diario.columns = ['data', 'nivel']

    nivel_diario['mes_dia'] = nivel_diario['data'].dt.strftime('%m-%d')

    estatisticas = nivel_diario.groupby('mes_dia')['nivel'].agg([
        ('minimo', 'min'),
        ('p10', lambda x: x.quantile(0.90)),
        ('p50', lambda x: x.quantile(0.50)),
        ('p90', lambda x: x.quantile(0.10)),
        ('maximo', 'max'),
        ('media', 'mean'),
        ('desvio_padrao', 'std')
    ]).reset_index()

    estatisticas['limite_superior'] = (
        estatisticas['media'] +
        estatisticas['desvio_padrao']
    )

    estatisticas['limite_inferior'] = (
        estatisticas['media'] -
        estatisticas['desvio_padrao']
    )

    return nome_estacao, P95, nivel_diario, estatisticas


# ============================================================
# INDICADORES
# ============================================================

def calcular_indicadores(nivel_diario):

    serie = nivel_diario['nivel'].dropna()

    if len(serie) < 8:
        return 0, 0, 0, 0, 0, "→ Estável"

    nivel_atual = serie.iloc[-1]

    percentil_serie = round(
        ((serie >= nivel_atual).sum() / len(serie)) * 100
    )

    ultima_data = nivel_diario['data'].max()
    mes_dia = ultima_data.strftime('%m-%d')

    amostra_sazonal = nivel_diario[
        nivel_diario['mes_dia'] == mes_dia
    ]['nivel'].dropna()

    if len(amostra_sazonal) > 0:
        percentil_sazonal = round(
            ((amostra_sazonal >= nivel_atual).sum() / len(amostra_sazonal)) * 100
        )
    else:
        percentil_sazonal = 0

    nivel_7d = serie.iloc[-8]

    variacao_m = nivel_atual - nivel_7d
    variacao_pct = (variacao_m / nivel_7d) * 100

    if variacao_m > 0.05:
        tendencia = "↑ Crescente"
    elif variacao_m < -0.05:
        tendencia = "↓ Decrescente"
    else:
        tendencia = "→ Estável"

    return (
        nivel_atual,
        percentil_sazonal,
        percentil_serie,
        variacao_m,
        variacao_pct,
        tendencia
    )


def configurar_eixo_x(fig, periodo):

    if periodo in ['15 dias', '1 mês']:
        fig.update_xaxes(tickformat="%d/%m", dtick="D2")

    elif periodo == '4 meses':
        fig.update_xaxes(tickformat="%b/%Y", dtick="M1")

    elif periodo == '12 meses':
        fig.update_xaxes(tickformat="%b/%Y", dtick="M2")

    elif periodo == 'Série completa':
        fig.update_xaxes(tickformat="%Y", dtick="M12")


def hover(nome):
    return f'{nome}: %{{y:.2f}} m<extra></extra>'


# ============================================================
# GRÁFICO PRINCIPAL
# ============================================================

def gerar_grafico(df_plot, nome_estacao, periodo, P95):

    fig = go.Figure()

    ocultar_percentis = periodo in ['12 meses', 'Série completa']
    mostrar_envelope = periodo not in ['12 meses', 'Série completa']

    cols_hist = ['minimo', 'p10', 'p50', 'p90', 'maximo']
    df_plot.loc[df_plot['nivel'].isna(), cols_hist] = pd.NA

    if mostrar_envelope:

        fig.add_trace(go.Scatter(
            x=df_plot['data'],
            y=df_plot['minimo'],
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            connectgaps=False,
            hoverinfo='skip'
        ))

        fig.add_trace(go.Scatter(
            x=df_plot['data'],
            y=df_plot['maximo'],
            mode='lines',
            fill='tonexty',
            fillcolor='rgba(176,196,222,0.20)',
            line=dict(width=0),
            name='Envelope histórico',
            connectgaps=False,
            hoverinfo='skip'
        ))

    fig.add_trace(go.Scatter(
        x=[df_plot['data'].min(), df_plot['data'].max()],
        y=[P95, P95],
        mode='lines',
        name='P95 histórica (série completa)',
        line=dict(color='red', width=2, dash='dot')
    ))

    series = {
        'MÁX': ('maximo', '#B08D57'),
        'P10': ('p10', '#F4C27A'),
        'P50': ('p50', '#9BC59D'),
        'P90': ('p90', '#E7A5A5'),
        'MIN': ('minimo', '#C7B3D8'),
        'NÍVEL': ('nivel', 'royalblue')
    }

    for nome, (col, cor) in series.items():

        visible = True

        if ocultar_percentis and nome != 'NÍVEL':
            visible = 'legendonly'

        fig.add_trace(go.Scatter(
            x=df_plot['data'],
            y=df_plot[col],
            mode='lines',
            name=nome,
            visible=visible,
            line=dict(
                color=cor,
                width=4 if nome == 'NÍVEL' else 2,
                dash='solid' if nome == 'NÍVEL' else 'dash'
            ),
            connectgaps=False,
            hovertemplate=hover(nome)
        ))

    fig.update_layout(
        title=f'{nome_estacao} - {periodo}',
        xaxis_title='Data',
        yaxis_title='Nível (m)',
        height=700,
        hovermode='x unified',
        template='plotly_white'
    )

    configurar_eixo_x(fig, periodo)

    return fig
```

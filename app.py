import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scipy.interpolate import PchipInterpolator
import numpy as np

st.set_page_config(
    page_title="Dashboard Hidrológico",
    layout="wide"
)

# ============================================================
# SUAVIZAÇÃO
# ============================================================

def smooth_curve(datas, valores, pontos=500):
    x = np.arange(len(datas))
    y = np.array(valores, dtype=float)

    mask = ~np.isnan(y)
    x_valid = x[mask]
    y_valid = y[mask]

    if len(x_valid) < 3:
        return datas, valores

    x_smooth = np.linspace(x_valid.min(), x_valid.max(), pontos)

    interpolador = PchipInterpolator(x_valid, y_valid)
    y_smooth = interpolador(x_smooth)

    datas_smooth = pd.to_datetime(
        np.interp(x_smooth, x, datas.astype(np.int64))
    )

    return datas_smooth, y_smooth


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

    # filtros de consistência
    df.loc[df['nivel'] > 20, 'nivel'] = pd.NA
    df.loc[df['chuva'] > 500, 'chuva'] = pd.NA

    nome_estacao = df['estacao'].dropna().iloc[0]

    # P95 (nível excedido 95% do tempo)
    P95 = df['nivel'].quantile(0.05)

    # preparação temporal
    df['data'] = df['datetime'].dt.floor('D')
    df['dia_ano'] = df['datetime'].dt.dayofyear

    # nível máximo diário
    nivel_diario = df.groupby('data')['nivel'].max().reset_index()
    nivel_diario['dia_ano'] = nivel_diario['data'].dt.dayofyear

    # estatísticas históricas
    estatisticas = nivel_diario.groupby('dia_ano')['nivel'].agg([
        ('minimo', 'min'),
        ('p10', lambda x: x.quantile(0.90)),
        ('p50', lambda x: x.quantile(0.50)),
        ('p90', lambda x: x.quantile(0.10)),
        ('maximo', 'max')
    ]).reset_index()

    return nome_estacao, P95, nivel_diario, estatisticas


# ============================================================
# GRÁFICO
# ============================================================

def gerar_grafico(df_plot, nome_estacao, periodo, P95):

    fig = go.Figure()

    # envelope histórico
    x_fill_min, y_fill_min = smooth_curve(df_plot['data'], df_plot['minimo'])
    x_fill_max, y_fill_max = smooth_curve(df_plot['data'], df_plot['maximo'])

    fig.add_trace(go.Scatter(
        x=x_fill_min,
        y=y_fill_min,
        line=dict(width=0),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=x_fill_max,
        y=y_fill_max,
        fill='tonexty',
        fillcolor='rgba(176,196,222,0.25)',
        line=dict(width=0),
        name='Envelope histórico'
    ))

    # séries
    series = {
        'MÁX': ('maximo', 'saddlebrown'),
        'P10': ('p10', 'darkorange'),
        'P50': ('p50', 'green'),
        'P90': ('p90', 'red'),
        'MIN': ('minimo', 'purple'),
        'NÍVEL': ('nivel', 'royalblue')
    }

    for nome, (col, cor) in series.items():

        x_s, y_s = smooth_curve(df_plot['data'], df_plot[col])

        fig.add_trace(go.Scatter(
            x=x_s,
            y=y_s,
            mode='lines',
            name=nome,
            line=dict(
                color=cor,
                width=4 if nome == 'NÍVEL' else 2,
                dash='solid' if nome == 'NÍVEL' else 'dash'
            )
        ))

    # P95
    fig.add_hline(
        y=P95,
        line_dash='dot',
        line_color='red',
        annotation_text=f'P95 = {P95:.2f} m'
    )

    fig.update_layout(
        title=f'{nome_estacao} - {periodo}',
        xaxis_title='Data',
        yaxis_title='Nível (m)',
        height=700,
        hovermode='x unified',
        template='plotly_white'
    )

    return fig


# ============================================================
# APP
# ============================================================

st.title("Dashboard Hidrológico")

arquivo = st.file_uploader(
    "Upload CSV da estação",
    type=['csv']
)

if arquivo:

    df = pd.read_csv(
        arquivo,
        encoding='latin1',
        sep=';'
    )

    nome_estacao, P95, nivel_diario, estatisticas = processar_dados(df)

    periodo = st.radio(
        "Selecione o período",
        ['15 dias', '1 mês', '4 meses', '12 meses'],
        horizontal=True
    )

    ultima_data = nivel_diario['data'].max()

    if periodo == '15 dias':
        inicio = ultima_data - pd.Timedelta(days=15)

    elif periodo == '1 mês':
        inicio = ultima_data - pd.DateOffset(months=1)

    elif periodo == '4 meses':
        inicio = ultima_data - pd.DateOffset(months=4)

    else:
        inicio = ultima_data - pd.DateOffset(years=1)

    observado = nivel_diario[
        (nivel_diario['data'] >= inicio) &
        (nivel_diario['data'] <= ultima_data)
    ]

    grafico = observado.merge(
        estatisticas,
        on='dia_ano',
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
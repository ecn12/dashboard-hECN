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
    y = np.array(valores, dtype=float)

    mask = ~np.isnan(y)

    datas_valid = pd.to_datetime(datas[mask])
    y_valid = y[mask]

    if len(y_valid) < 3:
        return datas, valores

    x = np.arange(len(datas_valid))
    x_smooth = np.linspace(x.min(), x.max(), pontos)

    interpolador = PchipInterpolator(x, y_valid)
    y_smooth = interpolador(x_smooth)

    datas_smooth = pd.date_range(
        start=datas_valid.min(),
        end=datas_valid.max(),
        periods=pontos
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

    # filtros
    df.loc[df['nivel'] > 20, 'nivel'] = pd.NA
    df.loc[df['chuva'] > 500, 'chuva'] = pd.NA

    nome_estacao = df['estacao'].dropna().iloc[0]

    # P95 da série histórica completa
    P95 = df['nivel'].quantile(0.05)

    df['data'] = df['datetime'].dt.floor('D')
    df['dia_ano'] = df['datetime'].dt.dayofyear

    # máximo diário
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
# EIXO X
# ============================================================

def configurar_eixo_x(fig, periodo):

    if periodo in ['15 dias', '1 mês']:
        fig.update_xaxes(
            tickformat="%d/%m",
            dtick="D2"
        )

    elif periodo == '4 meses':
        fig.update_xaxes(
            tickformat="%b/%Y",
            dtick="M1"
        )

    elif periodo == '12 meses':
        fig.update_xaxes(
            tickformat="%b/%Y",
            dtick="M2"
        )

    elif periodo == 'Série completa':
        fig.update_xaxes(
            tickformat="%Y",
            dtick="M12"
        )


# ============================================================
# GRÁFICO
# ============================================================

def gerar_grafico(df_plot, nome_estacao, periodo, P95):

    fig = go.Figure()

    # envelope histórico
    x_min, y_min = smooth_curve(df_plot['data'], df_plot['minimo'])
    x_max, y_max = smooth_curve(df_plot['data'], df_plot['maximo'])

    fig.add_trace(go.Scatter(
        x=x_min,
        y=y_min,
        line=dict(width=0),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=x_max,
        y=y_max,
        fill='tonexty',
        fillcolor='rgba(176,196,222,0.20)',
        line=dict(width=0),
        name='Envelope histórico'
    ))

    # P95 histórica
    fig.add_trace(go.Scatter(
        x=[df_plot['data'].min(), df_plot['data'].max()],
        y=[P95, P95],
        mode='lines',
        name='P95 histórica (série completa)',
        line=dict(
            color='red',
            width=2,
            dash='dot'
        )
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
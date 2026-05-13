import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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

    # filtros
    df.loc[df['nivel'] > 20, 'nivel'] = pd.NA
    df.loc[df['chuva'] > 500, 'chuva'] = pd.NA

    nome_estacao = df['estacao'].dropna().iloc[0]

    # P95 histórica da série completa
    P95 = df['nivel'].quantile(0.05)

    df['data'] = df['datetime'].dt.floor('D')
    df['dia_ano'] = df['datetime'].dt.dayofyear

    # máximo diário observado
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

    ocultar_percentis = periodo in ['12 meses', 'Série completa']

    # envelope histórico
    fig.add_trace(go.Scatter(
        x=df_plot['data'],
        y=df_plot['minimo'],
        line=dict(width=0),
        showlegend=False,
        connectgaps=False
    ))

    fig.add_trace(go.Scatter(
        x=df_plot['data'],
        y=df_plot['maximo'],
        fill='tonexty',
        fillcolor='rgba(176,196,222,0.20)',
        line=dict(width=0),
        name='Envelope histórico',
        connectgaps=False
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
        ),
        connectgaps=False
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
            connectgaps=False
        ))

    # eixo Y dinâmico
    if ocultar_percentis:
        y_max = max(
            df_plot['nivel'].dropna().max(),
            P95
        ) * 1.10

        fig.update_yaxes(range=[0, y_max])

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
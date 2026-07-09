import pandas as pd
import plotly.graph_objects as go

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
            marker=dict(size=0),
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
            marker=dict(size=0),
            name='Envelope histórico',
            connectgaps=False,
            hovertemplate=hover('Envelope histórico')
        ))

    fig.add_trace(go.Scatter(
        x=[df_plot['data'].min(), df_plot['data'].max()],
        y=[P95, P95],
        mode='lines',
        name='P95 histórica (série completa)',
        line=dict(color='red', width=2, dash='dot'),
        hovertemplate=hover('P95 histórica')
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
        template='plotly_white',
        xaxis=dict(hoverformat="%d/%m/%Y")
    )

    configurar_eixo_x(fig, periodo)

    return fig

def gerar_grafico_contexto(
    nivel_diario,
    estatisticas,
    P95,
    nome_estacao,
    periodo_contexto
):

    contexto = nivel_diario.dropna(subset=['nivel']).copy()

    ultima_data = contexto['data'].max()

    if periodo_contexto == '15 dias':
        inicio = ultima_data - pd.Timedelta(days=15)

    elif periodo_contexto == '1 mês':
        inicio = ultima_data - pd.DateOffset(months=1)

    elif periodo_contexto == '4 meses':
        inicio = ultima_data - pd.DateOffset(months=4)

    elif periodo_contexto == '12 meses':
        inicio = ultima_data - pd.DateOffset(years=1)

    else:
        inicio = contexto['data'].min()

    contexto = contexto[
        (contexto['data'] >= inicio) &
        (contexto['data'] <= ultima_data)
    ].copy()

    contexto = contexto.merge(
        estatisticas[
            [
                'mes_dia',
                'minimo',
                'maximo',
                'p10',
                'p50',
                'p90'
            ]
        ],
        on='mes_dia',
        how='left'
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=contexto['data'],
        y=contexto['p90'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))

    fig.add_trace(go.Scatter(
        x=contexto['data'],
        y=contexto['p10'],
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(100,180,100,0.20)',
        line=dict(width=0),
        name='Faixa de normalidade (P10–P90)',
        hoverinfo='skip'
    ))

    fig.add_trace(go.Scatter(
        x=contexto['data'],
        y=contexto['p50'],
        mode='lines',
        name='P50 sazonal',
        line=dict(
            color='#9BC59D',
            width=2,
            dash='dash'
        )
    ))

    fig.add_trace(go.Scatter(
        x=contexto['data'],
        y=contexto['maximo'],
        mode='lines',
        name='Máximo histórico',
        line=dict(
            color='#B08D57',
            width=2,
            dash='dash'
        )
    ))

    fig.add_trace(go.Scatter(
        x=contexto['data'],
        y=contexto['minimo'],
        mode='lines',
        name='Mínimo histórico',
        line=dict(
            color='#C7B3D8',
            width=2,
            dash='dash'
        )
    ))

    fig.add_trace(go.Scatter(
        x=contexto['data'],
        y=[P95] * len(contexto),
        mode='lines',
        name='Q95 histórica',
        line=dict(
            color='red',
            width=2,
            dash='dot'
        )
    ))

    fig.add_trace(go.Scatter(
    x=contexto['data'],
    y=contexto['nivel'],
    mode='lines',
    name='Nível observado',
    line=dict(
        color='royalblue',
        width=4
    ),
    connectgaps=False,
    hovertemplate=hover('Nível observado')
    ))

    fig.update_layout(
        title=f'{nome_estacao} - Contexto Hidrológico Sazonal ({periodo_contexto})',
        xaxis_title='Data',
        yaxis_title='Nível (m)',
        height=550,
        hovermode='x unified',
        template='plotly_white'
    )

    configurar_eixo_x(fig, periodo_contexto)

    return fig

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

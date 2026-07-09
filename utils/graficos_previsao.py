import plotly.graph_objects as go


def gerar_grafico_previsao(observado, nome_estacao):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=observado["data"],
            y=observado["nivel"],
            mode="lines+markers",
            name="Observado",
            line=dict(
                color="black",
                width=3
            ),
            marker=dict(size=6)
        )
    )

    fig.update_layout(

        title=f"Previsão Hidrológica - {nome_estacao}",

        template="plotly_white",

        height=600,

        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        ),

        xaxis_title="Data",

        yaxis_title="Nível (m)",

        legend=dict(
            orientation="h",
            y=1.02
        )

    )

    return fig

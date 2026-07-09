import pandas as pd
import plotly.graph_objects as go


def gerar_grafico_previsao(
    observado,
    estatisticas,
    P95,
    nome_estacao
):

    # ======================================================
    # PERÍODO FUTURO (7 dias)
    # ======================================================

    ultima_data = observado["data"].max()

    datas_futuras = pd.date_range(
        ultima_data + pd.Timedelta(days=1),
        periods=7,
        freq="D"
    )

    # Linha provisória (horizontal)
    ultimo_nivel = observado["nivel"].iloc[-1]

    previsao = pd.DataFrame({
        "data": datas_futuras,
        "nivel": [ultimo_nivel] * 7
    })

    previsao["mes_dia"] = previsao["data"].dt.strftime("%m-%d")

    previsao = previsao.merge(
    estatisticas,
    on="mes_dia",
    how="left"
)

    previsao["limite_superior"] = (
        previsao["media"] +
        previsao["desvio_padrao"]
    )

    previsao["limite_inferior"] = (
        previsao["media"] -
        previsao["desvio_padrao"]
    )

# ======================================================
# OBSERVADO
# ======================================================

fig = go.Figure()

    # ------------------------------------------------------

    fig.add_trace(

        go.Scatter(

            x=observado["data"],
            y=observado["nivel"],

            mode="lines",

            name="Observado",

            line=dict(
                color="black",
                width=3
            )

        )

    )

    # ======================================================
    # PREVISÃO (TEMPORÁRIA)
    # ======================================================

    fig.add_trace(

        go.Scatter(

            x=previsao["data"],
            y=previsao["nivel"],

            mode="lines",

            name="Previsão",

            line=dict(
                color="royalblue",
                width=3,
                dash="dot"
            )

        )

    )

    # ======================================================
    # LINHA MÉDIA
    # ======================================================

    fig.add_trace(

        go.Scatter(

            x=previsao["data"],
            y=previsao["media"],

            mode="lines",

            name="Média histórica",

            line=dict(
                color="navy",
                width=2
            )

        )

    )

    # ======================================================
    # FAIXA NORMAL
    # ======================================================

    fig.add_trace(

        go.Scatter(

            x=previsao["data"],
            y=previsao["limite_superior"],

            mode="lines",

            line=dict(width=0),

            showlegend=False

        )

    )

    fig.add_trace(

        go.Scatter(

            x=previsao["data"],
            y=previsao["limite_inferior"],

            mode="lines",

            fill="tonexty",

            fillcolor="rgba(0,100,255,0.20)",

            line=dict(width=0),

            name="Faixa de normalidade histórica"

        )

    )

    # ======================================================
    # Q95
    # ======================================================

    fig.add_hline(

        y=P95,

        line_color="orange",

        line_width=2,

        annotation_text="Q95",

        annotation_position="bottom right"

    )

    # ======================================================
    # HOJE
    # ======================================================

    fig.add_vline(

        x=ultima_data,

        line_dash="dash",

        line_color="gray"

    )

    # ======================================================

    fig.update_layout(

        title=f"Previsão Hidrológica - {nome_estacao}",

        template="plotly_white",

        height=650,

        legend=dict(
            orientation="h",
            y=1.05
        ),

        xaxis_title="",

        yaxis_title="Nível (m)"

    )

    return fig

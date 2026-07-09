import pandas as pd
import plotly.graph_objects as go


def gerar_grafico_previsao(
    observado,
    estatisticas,
    P95,
    nome_estacao
):

    # =====================================================
    # PREVISÃO TEMPORÁRIA (7 dias)
    # =====================================================

    ultima_data = observado["data"].max()

    datas_futuras = pd.date_range(
        start=ultima_data + pd.Timedelta(days=1),
        periods=7,
        freq="D"
    )

    ultimo_nivel = observado["nivel"].iloc[-1]

    previsao = pd.DataFrame({
        "data": datas_futuras,
        "nivel": [ultimo_nivel] * len(datas_futuras)
    })

    previsao["mes_dia"] = previsao["data"].dt.strftime("%m-%d")

    previsao = previsao.merge(
        estatisticas,
        on="mes_dia",
        how="left"
    )

    # =====================================================
    # CASO NÃO EXISTAM AS COLUNAS DE LIMITES
    # =====================================================

    if (
        "limite_superior" not in previsao.columns
        and
        "desvio_padrao" in previsao.columns
    ):

        previsao["limite_superior"] = (
            previsao["media"] +
            previsao["desvio_padrao"]
        )

        previsao["limite_inferior"] = (
            previsao["media"] -
            previsao["desvio_padrao"]
        )

    # =====================================================
    # FIGURA
    # =====================================================

    fig = go.Figure()

    # =====================================================
    # OBSERVADO
    # =====================================================

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

    # =====================================================
    # PREVISÃO
    # =====================================================

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

    # =====================================================
    # MÉDIA
    # =====================================================

    if "media" in previsao.columns:

        fig.add_trace(
            go.Scatter(
                x=previsao["data"],
                y=previsao["media"],
                mode="lines",
                name="Média",
                line=dict(
                    color="navy",
                    width=2
                )
            )
        )

    # =====================================================
    # FAIXA DE NORMALIDADE
    # =====================================================

    if (
        "limite_superior" in previsao.columns
        and
        "limite_inferior" in previsao.columns
    ):

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
                name="Faixa de normalidade"
            )
        )

    # =====================================================
    # Q95
    # =====================================================

    fig.add_hline(
        y=P95,
        line_color="orange",
        line_width=2,
        annotation_text="Q95"
    )

    # =====================================================
    # HOJE
    # =====================================================

    fig.add_vline(
        x=ultima_data,
        line_dash="dash",
        line_color="gray"
    )

    # =====================================================
    # LAYOUT
    # =====================================================

    fig.update_layout(

        title=f"Previsão Hidrológica - {nome_estacao}",

        template="plotly_white",

        height=650,

        legend=dict(
            orientation="h",
            y=1.02
        ),

        xaxis_title="",

        yaxis_title="Nível (m)"

    )

    return fig

import pandas as pd
import plotly.graph_objects as go


# ==========================================================
# PREPARA DADOS OBSERVADOS
# ==========================================================

def preparar_historico(
    observado,
    estatisticas
):

    historico = observado.copy()

    historico["mes_dia"] = (
        historico["data"]
        .dt.strftime("%m-%d")
    )

    historico = historico.merge(
        estatisticas,
        on="mes_dia",
        how="left"
    )

    return historico


# ==========================================================
# PREPARA PREVISÃO (TEMPORÁRIA)
# FUTURAMENTE SERÁ SUBSTITUÍDA PELO HOLT
# ==========================================================

def preparar_previsao(
    historico,
    estatisticas
):

    ultima_data = historico["data"].max()

    ultimo_nivel = historico["nivel"].iloc[-1]

    # Primeiro ponto da previsão é o último observado
    datas = pd.date_range(
        start=ultima_data,
        periods=8,
        freq="D"
    )

    previsao = pd.DataFrame({

        "data": datas,

        "nivel": [ultimo_nivel] * len(datas)

    })

    previsao["mes_dia"] = (
        previsao["data"]
        .dt.strftime("%m-%d")
    )

    previsao = previsao.merge(

        estatisticas,

        on="mes_dia",

        how="left"

    )

    return previsao


# ==========================================================
# CALCULA LIMITES DO EIXO Y
# ==========================================================

def calcular_limites_y(
    historico,
    previsao,
    P95
):

    y_min = min(

        historico["nivel"].min(),

        previsao["nivel"].min(),

        historico["p90"].min(),

        previsao["p90"].min(),

        P95

    )

    y_max = max(

        historico["nivel"].max(),

        previsao["nivel"].max(),

        historico["p10"].max(),

        previsao["p10"].max()

    )

    margem = (y_max - y_min) * 0.10

    return (

        y_min - margem,

        y_max + margem

    )


# ==========================================================
# GRÁFICO
# ==========================================================

def gerar_grafico_previsao(
    observado,
    estatisticas,
    P95,
    nome_estacao
):

    historico = preparar_historico(
        observado,
        estatisticas
    )

    previsao = preparar_previsao(
        historico,
        estatisticas
    )

    y_min, y_max = calcular_limites_y(
        historico,
        previsao,
        P95
    )

    

    ultima_data = historico["data"].max()

    fig = go.Figure()

    # ==========================================================
    # FAIXA DE NORMALIDADE (HISTÓRICO)
    # ==========================================================

    fig.add_trace(
        go.Scatter(
            x=historico["data"],
            y=historico["p10"],
            mode="lines",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=historico["data"],
            y=historico["p90"],
            mode="lines",
            fill="tonexty",
            fillcolor="rgba(70,130,180,0.08)",
            line=dict(width=0),
            name="Faixa de normalidade"
        )
    )

    # ==========================================================
    # FAIXA DE NORMALIDADE (PREVISÃO)
    # ==========================================================

    fig.add_trace(
        go.Scatter(
            x=previsao["data"],
            y=previsao["p10"],
            mode="lines",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=previsao["data"],
            y=previsao["p90"],
            mode="lines",
            fill="tonexty",
            fillcolor="rgba(70,130,180,0.08)",
            line=dict(width=0),
            showlegend=False
        )
    )

    # ==========================================================
    # MÉDIA HISTÓRICA
    # ==========================================================

    fig.add_trace(
        go.Scatter(
            x=pd.concat([
                historico["data"],
                previsao["data"].iloc[1:]
            ]),
            y=pd.concat([
                historico["media"],
                previsao["media"].iloc[1:]
            ]),
            mode="lines",
            name="Média",
            line=dict(
                color="royalblue",
                width=1.5
            )
        )
    )

    # ==========================================================
    # OBSERVADO
    # ==========================================================

    fig.add_trace(
        go.Scatter(
            x=historico["data"],
            y=historico["nivel"],
            mode="lines",
            name="Observado",
            line=dict(
                color="black",
                width=3
            )
        )
    )

    # ==========================================================
    # PREVISÃO
    # ==========================================================

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

    # ==========================================================
    # Q95
    # ==========================================================

    fig.add_hline(
        y=P95,
        line=dict(
            color="orange",
            width=2
        ),
        annotation_text="Q95",
        annotation_position="bottom right"
    )

    # ==========================================================
    # HOJE
    # ==========================================================

    fig.add_vline(
        x=ultima_data,
        line_dash="dash",
        line_color="gray",
        line_width=1
    )

    # ==========================================================
    # LAYOUT
    # ==========================================================

    fig.update_layout(

        title=f"Previsão Hidrológica - {nome_estacao}",

        template="plotly_white",

        height=650,

        hovermode="x unified",

        legend=dict(
            orientation="h",
            y=1.04,
            x=0
        ),

        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        ),

        xaxis_title="",

        yaxis_title="Nível (m)"

    )

    fig.update_yaxes(
        range=[y_min, y_max]
    )

    return fig

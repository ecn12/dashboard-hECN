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

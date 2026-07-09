import pandas as pd


def processar_dados(df):

    # ==========================================================
    # DETECTA O TIPO DE ARQUIVO
    # ==========================================================

    colunas = [c.upper() for c in df.columns]

    eh_ana = "VAZAO" in colunas

    # ==========================================================
    # ARQUIVOS ANA (VAZÃO DIÁRIA)
    # ==========================================================

    if eh_ana:

        df.columns = ["estacao", "data", "chuva", "nivel"]

        df = df.replace(["SD", "9999"], pd.NA)

        df["data"] = pd.to_datetime(
            df["data"],
            format="%d/%m/%Y"
        )

        df["chuva"] = pd.to_numeric(
            df["chuva"],
            errors="coerce"
        )

        df["nivel"] = (
            df["nivel"]
            .astype(str)
            .str.replace(",", ".", regex=False)
        )

        df["nivel"] = pd.to_numeric(
            df["nivel"],
            errors="coerce"
        )

        nome_estacao = str(df["estacao"].iloc[0])

        P95 = df["nivel"].quantile(0.05)

        nivel_diario = (
            df[["data", "nivel"]]
            .sort_values("data")
            .copy()
        )

    # ==========================================================
    # ARQUIVOS CEMADEN / INEA (NÍVEL SUBDIÁRIO)
    # ==========================================================

    else:

        df.columns = ["estacao", "datetime", "chuva", "nivel"]

        df = df.replace(["SD", "9999"], pd.NA)

        df["datetime"] = pd.to_datetime(
            df["datetime"],
            format="%d/%m/%Y %H:%M"
        )

        df["chuva"] = pd.to_numeric(
            df["chuva"],
            errors="coerce"
        )

        df["nivel"] = pd.to_numeric(
            df["nivel"],
            errors="coerce"
        )

        df.loc[df["nivel"] > 20, "nivel"] = pd.NA
        df.loc[df["chuva"] > 500, "chuva"] = pd.NA

        nome_estacao = str(df["estacao"].iloc[0])

        P95 = df["nivel"].quantile(0.05)

        df["data"] = df["datetime"].dt.floor("D")

        nivel_diario = (
            df.groupby("data")["nivel"]
            .max()
            .reset_index()
        )

    # ==========================================================
    # COMPLETA A SÉRIE DIÁRIA
    # ==========================================================

    datas = pd.date_range(
        nivel_diario["data"].min(),
        nivel_diario["data"].max(),
        freq="D"
    )

    nivel_diario = (
        nivel_diario
        .set_index("data")
        .reindex(datas)
        .rename_axis("data")
        .reset_index()
    )

    nivel_diario["mes_dia"] = (
        nivel_diario["data"]
        .dt.strftime("%m-%d")
    )

    # ==========================================================
    # ESTATÍSTICAS HISTÓRICAS
    # ==========================================================

    estatisticas = (
        nivel_diario
        .groupby("mes_dia")["nivel"]
        .agg(
            minimo="min",
            p10=lambda x: x.quantile(0.90),
            p50=lambda x: x.quantile(0.50),
            p90=lambda x: x.quantile(0.10),
            maximo="max",
            media="mean",
            desvio_padrao="std"
        )
        .reset_index()
    )

    estatisticas["limite_superior"] = (
        estatisticas["media"] +
        estatisticas["desvio_padrao"]
    )

    estatisticas["limite_inferior"] = (
        estatisticas["media"] -
        estatisticas["desvio_padrao"]
    )

    return (
        nome_estacao,
        P95,
        nivel_diario,
        estatisticas
    )

import pandas as pd
def processar_dados(df):

    df.columns = ['estacao', 'datetime', 'chuva', 'nivel']

    df = df.replace(['SD', '9999'], pd.NA)

    df['datetime'] = pd.to_datetime(
        df['datetime'],
        format='%d/%m/%Y %H:%M'
    )

    df['chuva'] = pd.to_numeric(df['chuva'], errors='coerce')
    df['nivel'] = pd.to_numeric(df['nivel'], errors='coerce')

    df.loc[df['nivel'] > 20, 'nivel'] = pd.NA
    df.loc[df['chuva'] > 500, 'chuva'] = pd.NA

    nome_estacao = df['estacao'].dropna().iloc[0]

    P95 = df['nivel'].quantile(0.05)

    df['data'] = df['datetime'].dt.floor('D')

    nivel_diario = df.groupby('data')['nivel'].max()

    datas_completas = pd.date_range(
        start=nivel_diario.index.min(),
        end=nivel_diario.index.max(),
        freq='D'
    )

    nivel_diario = nivel_diario.reindex(datas_completas)

    nivel_diario = nivel_diario.reset_index()
    nivel_diario.columns = ['data', 'nivel']

    nivel_diario['mes_dia'] = nivel_diario['data'].dt.strftime('%m-%d')

    estatisticas = nivel_diario.groupby('mes_dia')['nivel'].agg([
        ('minimo', 'min'),
        ('p10', lambda x: x.quantile(0.90)),
        ('p50', lambda x: x.quantile(0.50)),
        ('p90', lambda x: x.quantile(0.10)),
        ('maximo', 'max'),
        ('media', 'mean'),
        ('desvio_padrao', 'std')
    ]).reset_index()

    estatisticas['limite_superior'] = (
        estatisticas['media'] +
        estatisticas['desvio_padrao']
    ).rolling(7, center=True, min_periods=1).mean().round(2)

    estatisticas['limite_inferior'] = (
        estatisticas['media'] -
        estatisticas['desvio_padrao']
    ).rolling(7, center=True, min_periods=1).mean().round(2)

    return nome_estacao, P95, nivel_diario, estatisticas


import streamlit as st


def mostrar_card(
    nivel_atual,
    percentil_sazonal,
    percentil_serie,
    variacao_m,
    variacao_pct,
    tendencia
):

    # Define cor da tendência
    if "Crescente" in tendencia:
        cor = "#1a7f37"
    elif "Decrescente" in tendencia:
        cor = "#c62828"
    else:
        cor = "#1f4e79"

    st.markdown(
        f"""
        <div style="
            background:white;
            border:1px solid #d9d9d9;
            border-radius:12px;
            padding:18px;
            box-shadow:0 2px 6px rgba(0,0,0,0.08);
        ">

        <div style="
            font-size:28px;
            font-weight:700;
            color:#1f4e79;
            text-align:center;
            margin-bottom:18px;
        ">
            Situação Atual
        </div>

        <div style="font-size:15px;color:#555;">
            Nível Atual
        </div>

        <div style="
            font-size:40px;
            font-weight:700;
            margin-bottom:22px;
        ">
            {nivel_atual:.2f} m
        </div>

        <table style="
            width:100%;
            font-size:16px;
            border-collapse:collapse;
            margin-bottom:20px;
        ">

            <tr>
                <td>Percentil Sazonal</td>
                <td style="text-align:right;"><b>P{percentil_sazonal}</b></td>
            </tr>

            <tr>
                <td style="padding-top:8px;">Percentil Série</td>
                <td style="padding-top:8px;text-align:right;">
                    <b>P{percentil_serie}</b>
                </td>
            </tr>

        </table>

        <div style="
            font-size:15px;
            color:#555;
            margin-bottom:4px;
        ">
            Variação (7 dias)
        </div>

        <div style="
            font-size:22px;
            font-weight:600;
            margin-bottom:18px;
        ">
            {variacao_m:+.2f} m ({variacao_pct:+.1f}%)
        </div>

        <div style="
            font-size:15px;
            color:#555;
            margin-bottom:4px;
        ">
            Tendência
        </div>

        <div style="
            font-size:24px;
            font-weight:700;
            color:{cor};
        ">
            {tendencia}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

import streamlit as st


def mostrar_card(
    nivel_atual,
    percentil_sazonal,
    percentil_serie,
    variacao_m,
    variacao_pct,
    tendencia
):

    # -------------------------
    # Cor da tendência
    # -------------------------

    if "Crescente" in tendencia:
        cor_tendencia = "#1a7f37"

    elif "Decrescente" in tendencia:
        cor_tendencia = "#c62828"

    else:
        cor_tendencia = "#1f4e79"

    # -------------------------
    # Cor da variação percentual
    # -------------------------

    if variacao_pct > 0:

        cor_variacao = "#1a7f37"
        seta = "↑"

    elif variacao_pct < 0:

        cor_variacao = "#c62828"
        seta = "↓"

    else:

        cor_variacao = "#666666"
        seta = "→"

    st.markdown(
        f"""
<div style="
background:white;
border:1px solid #d9d9d9;
border-radius:12px;
padding:18px;
box-shadow:0 2px 6px rgba(0,0,0,.08);
">

<div style="
text-align:center;
font-size:28px;
font-weight:700;
color:#1f4e79;
margin-bottom:20px;
">

Situação Atual

</div>

<div style="font-size:15px;color:#666;">
Nível Atual
</div>

<div style="
font-size:38px;
font-weight:700;
margin-bottom:20px;
">

{nivel_atual:.2f} m

</div>

<hr style="margin:10px 0 18px 0;">

<div style="display:flex;justify-content:space-between;font-size:16px;margin-bottom:10px;">
<span>Percentil Sazonal</span>
<b>P{percentil_sazonal}</b>
</div>

<div style="display:flex;justify-content:space-between;font-size:16px;margin-bottom:18px;">
<span>Percentil Série</span>
<b>P{percentil_serie}</b>
</div>

<hr style="margin:10px 0 18px 0;">

<div style="font-size:15px;color:#666;">
Variação (7 dias)
</div>

<div style="
font-size:18px;
font-weight:600;
margin-top:4px;
">

{variacao_m:+.2f} m

</div>

<div style="
display:inline-block;
margin-top:8px;
padding:4px 10px;
border-radius:20px;
background:{cor_variacao}22;
color:{cor_variacao};
font-weight:600;
font-size:15px;
">

{seta} {variacao_pct:+.1f}%

</div>

<hr style="margin:18px 0 18px 0;">

<div style="font-size:15px;color:#666;">
Tendência
</div>

<div style="
font-size:20px;
font-weight:700;
margin-top:4px;
color:{cor_tendencia};
">

{tendencia}

</div>

</div>
""",
        unsafe_allow_html=True
    )

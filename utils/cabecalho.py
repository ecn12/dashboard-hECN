import streamlit as st


def mostrar_cabecalho(
    rio,
    estacao,
    operador,
    municipio,
    estado,
    redec,
    tipo,
    ultima_atualizacao
):

    st.markdown(
        f"""
# HECN – Plataforma Hidrológica

## {rio.upper()}

### Estação {estacao} — Operador: {operador}

📍 {municipio} • {estado} • REDEC {redec}

📡 {tipo}

🕒 Atualizado em {ultima_atualizacao.strftime('%d/%m/%Y às %H:%M')}

---
""",
        unsafe_allow_html=True
    )

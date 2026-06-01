import streamlit as st

st.set_page_config(
    page_title="Dashboard Hidrológico",
    layout="wide"
)

st.title("Dashboard Hidrológico")

st.markdown("""
## Página Inicial

Bem-vindo ao Dashboard Hidrológico.

Utilize o menu lateral para acessar a estação disponível.
""")

st.success("Estação disponível: Quizanga")

st.write("Versão V1.1 - Home")

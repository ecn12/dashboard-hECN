import streamlit as st

pagina = st.sidebar.radio(
    "Navegação",
    ["Home", "Quizanga"]
)

if pagina == "Home":

    st.title("Dashboard Hidrológico")

    st.write("Página inicial")

else:

    st.title("Quizanga")

    # aqui entra o dashboard atual

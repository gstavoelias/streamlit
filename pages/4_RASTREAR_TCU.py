import streamlit as st
from server import Server

st.set_page_config(page_title="Rastrear TCU TECSCI", page_icon="icon.ico", layout="wide")

with st.sidebar:
    st.image("logo-dark.png")

st.header("Rastrear TCU TECSCI")
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.stop()

st.header("WIP")
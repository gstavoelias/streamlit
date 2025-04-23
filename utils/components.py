import streamlit as st
from typing import Callable, List
from requests import Response

def render_header(page_title: str) -> None:
    st.set_page_config(page_title=page_title, page_icon="assets/icon.ico", layout="wide")
    with st.sidebar:
        st.image("assets/logo-dark.png")
    st.title(page_title)
    
    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        st.warning("Você precisa estar logado para acessar esta página.")
        st.stop()

def render_request_response(response: Response) -> None:
    if response.status_code == 201:
        st.success("Enviado com sucesso!")
    else:
        st.error(f"Erro: {response.status_code} - {response.text}")

def load_data(key: str, func: Callable[[], List]) -> List:
    if key not in st.session_state:
        st.session_state[key] = func()
    return st.session_state[key]



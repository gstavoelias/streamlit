import streamlit as st
import plotly.express as px
import pandas as pd
from server import Server

# Configuração da página
st.set_page_config(
    page_title="Banco de Dados TECSCI",
    page_icon="icon.ico",
    layout="wide"
)

# Inicializa o servidor
server = Server()

# Título do dashboard
st.title("HOME")

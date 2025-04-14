import streamlit as st
import pandas as pd
from server import Server

st.set_page_config(page_title="Adicionar RFT/Manutenção", page_icon="icon.ico", layout="wide")

# Sidebar
with st.sidebar:
    st.image("logo-dark.png")

st.title("Adicionar RFT/Manutenção")

# Inicializa servidor
if "server" not in st.session_state:
    st.session_state.server = Server("http://127.0.0.1:8087/api/v1.0/")
server = st.session_state.server

# Utilidade para exibir mensagens
def show_response(response):
    if response.status_code == 201:
        st.success("Enviado com sucesso!")
    else:
        st.error(f"Erro: {response.status_code} - {response.text}")

# Cache em session_state para os dados
def load_data_once(key, func):
    if key not in st.session_state:
        st.session_state[key] = func()
    return st.session_state[key]

# Dados carregados apenas uma vez
erros = load_data_once("erros", server.get_erro)
operadores = load_data_once("operadores", server.get_operators)
etapas = load_data_once("etapas", server.get_etapa)
rfts = load_data_once("rfts", server.get_rft)
solucoes = load_data_once("solucoes", server.get_solucao)

# Mapas
erro_map = {f"{e['etapa']} - {e['nome']}": e["id"] for e in erros}
operador_map = {o["nome"]: o["id"] for o in operadores}
etapas_map = {e["nome"]: e["id"] for e in etapas}
rft_map = {
    f"{r['controladora_id']} - {r['erro_id']['nome']} - {r['horario'].split('T')[0]}": r["id"]
    for r in rfts
}
solucao_map = {s["nome"]: s["id"] for s in solucoes}

# RFT
with st.expander("RFT"):
    erro_selecionado = st.selectbox("Erro", sorted(erro_map.keys()), help="Não encontrou o erro? Adicione abaixo.")
    serial_number = st.text_input("Número de série da TCU")
    operador_selecionado = st.selectbox("Operador", sorted(operador_map.keys()))
    data_selecionada_rft = st.date_input("Data", format="DD/MM/YYYY", key="data_rft")

    if st.button("ENVIAR", type="primary", key="post_rft"):
        response = server.post_rft(
            serial_number,
            operador_map[operador_selecionado],
            erro_map[erro_selecionado],
            data_selecionada_rft.isoformat()
        )
        show_response(response)

# ERRO
with st.expander("ERRO"):
    etapa_selecionada = st.selectbox("Etapa", sorted(etapas_map.keys()))
    erro_nome = st.text_input("Nome do Erro")
    if st.button("ENVIAR", type="primary", key="post_erro"):
        response = server.post_erro(etapas_map[etapa_selecionada], erro_nome)
        show_response(response)

# MANUTENÇÃO
with st.expander("MANUTENÇÃO"):
    rft_selecionado = st.selectbox("RFT", sorted(rft_map.keys()))
    tecnico_selecionado = st.selectbox("Técnico", sorted(operador_map.keys()))
    solucao_selecionada = st.selectbox("Solução", sorted(solucao_map.keys()))
    data_selecionada_man = st.date_input("Data", format="DD/MM/YYYY", key="data_manutencao")
    duracao = st.text_input("Duração (s)")

    if st.button("ENVIAR", type="primary", key="post_manutencao"):
        try:
            response = server.post_manutencao(
                operador_map[tecnico_selecionado],
                rft_map[rft_selecionado],
                solucao_map[solucao_selecionada],
                data_selecionada_man.isoformat(),
                float(duracao)
            )
            show_response(response)
        except ValueError:
            st.warning("A duração precisa ser um número válido.")

# SOLUÇÃO
with st.expander("SOLUÇÃO"):
    sol_nome = st.text_input("Nome da Solução")
    if st.button("ENVIAR", type="primary", key="post_solucao"):
        response = server.post_solucao(sol_nome)
        show_response(response)

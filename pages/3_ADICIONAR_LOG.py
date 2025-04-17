import streamlit as st
import pandas as pd

st.set_page_config(page_title="Adicionar RFT/Manutenção", page_icon="icon.ico", layout="wide")

# Sidebar
with st.sidebar:
    st.image("logo-dark.png")

st.title("Adicionar RFT/Manutenção")
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.stop()

# Inicializa servidor
api = st.session_state.api


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
erros = load_data_once("erros", api.get_erro)
operadores = load_data_once("operadores", api.get_operators)
etapas = load_data_once("etapas", api.get_etapa)
rfts = load_data_once("rfts", api.get_rft)
solucoes = load_data_once("solucoes", api.get_solucao)
materiais = load_data_once("materiais", api.get_materials)
manutencoes = load_data_once("manutencoes", api.get_manutencao)

erro_map = {f"{e['etapa']} - {e['nome']}": e["id"] for e in erros}
operador_map = {o["nome"]: o["id"] for o in operadores}
etapas_map = {e["nome"]: e["id"] for e in etapas}
rft_map = {
    f"{r['controladora_id']} - {r['erro_id']['nome']} - {r['horario'].split('T')[0]}": r["id"]
    for r in rfts
}
solucao_map = {s["nome"]: s["id"] for s in solucoes}
materials_map = {
    f"{m['id']} - {m['nome']}": m["id"] for m in materiais
}
manutencoes_map = {
    f"{m['rft']['controladora_id']} - {m['solucao']['nome']} - {m['horario'].split('T')[0]}": m["id"]
    for m in manutencoes
}
# RFT
with st.expander("RFT"):
    erro_selecionado = st.selectbox("Erro", sorted(erro_map.keys()), help="Não encontrou o erro? Adicione abaixo.")
    serial_number = st.text_input("Número de série da TCU")
    operador_selecionado = st.selectbox("Operador", sorted(operador_map.keys()))
    data_selecionada_rft = st.date_input("Data", format="DD/MM/YYYY", key="data_rft")

    if st.button("ENVIAR", type="primary", key="post_rft"):
        response = api.post_rft(
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
        response = api.post_erro(etapas_map[etapa_selecionada], erro_nome)
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
            response = api.post_manutencao(
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
        response = api.post_solucao(sol_nome)
        show_response(response)


with st.expander("MATERIAIS"):
    id = st.text_input("Código")
    nome  = st.text_input("Nome")
    if st.button("ENVIAR", type="primary", key="post_material"):
        response = api.post_material(id, nome)
        show_response(response)

with st.expander("PERDAS"):
    material_selecionado = st.selectbox("Material", options=sorted(materials_map.keys()))
    manutencao_selecionada = st.selectbox("Manutenção", options=sorted(manutencoes_map.keys()))
    quantidade = st.text_input("Quantidade")
    if st.button("ENVIAR", type="primary", key="post_perdas"):
        try:
            response = api.post_perdas(materials_map[material_selecionado], manutencoes_map[manutencao_selecionada], int(quantidade))
            show_response(response)
        except ValueError:
            st.warning("A quantidade precisa ser um número válido.")
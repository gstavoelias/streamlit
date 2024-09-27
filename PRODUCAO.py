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
st.title("Dashboard - Produção")

# Sidebar para localizar o TCU
with st.sidebar:
    st.image("logo-dark.png")
    st.write("#")
    st.write("#")

    # Campo de texto para localizar o TCU
    text_input = st.text_input("Localizar TCU:", placeholder="Digite o Número de Série")

    # Botão de pesquisa
    if st.button("Pesquisar", type="primary"):
        # Carregar os dados do servidor e armazenar no session_state para evitar múltiplas requisições
        df = server.get_tcu_history(text_input)
        st.session_state['df'] = df
        st.session_state['pesquisar_clicked'] = True

    # Verifica se o botão "Pesquisar" foi clicado e o DataFrame existe no session_state
    if 'pesquisar_clicked' in st.session_state and st.session_state['pesquisar_clicked']:
        st.write("## Histórico do TCU")
        st.dataframe(st.session_state['df'])
        
        # Exibir campos para alterar a localização da TCU
        st.write("## Alterar localização da TCU:")
        col1, col2 = st.columns(2)
        
        with col1:
            # Verifica se a lista de locais já foi buscada
            if 'locals' not in st.session_state:
                st.session_state['locals'] = server.get_locals()
            status = st.selectbox("Local", [local["nome"] for local in st.session_state['locals']], key="status_selectbox")
        
        with col2:
            # Verifica se a lista de operadores já foi buscada
            if 'operators' not in st.session_state:
                st.session_state['operators'] = server.get_operators()
            operador = st.selectbox("Operador", [operator["nome"] for operator in st.session_state['operators']], key="operador_selectbox")
        
        # Confirmar a seleção de operador e status
        if st.button("Confirmar", type="secondary"):
            operador_id = None
            local_id = None
            for operator in st.session_state['operators']:
                if operator["nome"] == operador:
                    operador_id = operator["id"]
            for local in st.session_state['locals']:
                if local["nome"] == status:
                    local_id = local["id"]
            
            # Chamar a função para alterar o status
            response = server.change_tcu_status(text_input, operador_id, local_id)
            
            # Atualizar os dados após a mudança de status
            if response['success']:
                # Atualizar os dados após a confirmação
                st.session_state['df'] = server.get_tcu_history(text_input)
                st.session_state['status_data'] = server.get_status_data()
                st.write("Status alterado com sucesso!")
            else:
                st.write(f"Erro ao alterar status: {response['message']}")

# Verifica se os dados de status já foram buscados
if 'status_data' not in st.session_state:
    st.session_state['status_data'] = server.get_status_data()


# Gráfico de pizza com a localização dos TCUs
st.write("## Localização dos TCUs:")
data = st.session_state['status_data'].groupby("status.status_id.nome").size().reset_index(name='counts')
pie_chart = px.pie(data, names="status.status_id.nome", values="counts")
st.plotly_chart(pie_chart, use_container_width=True)

# Expand para mostrar os dados da base de testes
with st.expander(f"BASE DE DADOS - {st.session_state['status_data'].shape[0]} TCUs"):
    st.dataframe(st.session_state['status_data'])

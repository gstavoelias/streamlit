import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from server import Server
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

st.set_page_config(
    page_title="Banco de Dados TECSCI",
    page_icon="icon.ico",
    layout="wide"
)

st.title("Dashboard - Burn In")
with st.sidebar:
    st.image("logo-dark.png")
    st.write("#")
    st.write("#")

server = Server()

# Criar variável no session_state para armazenar o período selecionado
if "selected_period" not in st.session_state:
    st.session_state.selected_period = "SEMANA"

def get_start_date(period):
    """Retorna a data inicial com base no período selecionado"""
    hoje = datetime.today()

    if period == "SEMANA":
        inicio = hoje - timedelta(days=hoje.weekday())  # Segunda-feira da semana atual
    elif period == "MÊS":
        inicio = hoje.replace(day=1)  # Primeiro dia do mês atual
    elif period == "SEMESTRE":
        mes_atual = hoje.month
        primeiro_mes_do_semestre = 1 if mes_atual <= 6 else 7  # Janeiro ou Julho
        inicio = hoje.replace(month=primeiro_mes_do_semestre, day=1)
    elif period == "ANO":
        inicio = hoje.replace(month=1, day=1)  # Primeiro dia do ano atual
    else:  # TOTAL → Sem limite inferior
        return None

    return inicio

def update_df():
    """Atualiza o DataFrame com base na opção selecionada"""
    period = st.session_state.selected_period
    start_date = get_start_date(period) if period else get_start_date("SEMANA")
    st.write(server.token)
    try:
        st.session_state.df = server.get_burnin_data(start_date)
    except Exception as e:
        st.write(e.args)

# Executa a primeira carga de dados
update_df()

st.write("## Testes realizados por dia:")
st.selectbox(
    label="Visualização:", 
    options=["SEMANA", "MÊS", "SEMESTRE", "ANO", "TOTAL"], 
    index=["SEMANA", "MÊS", "SEMESTRE", "ANO", "TOTAL"].index(st.session_state.selected_period),
    key="selected_period",
    label_visibility="hidden",
    on_change=update_df
)

df = st.session_state.df
data = df.groupby(df["horario"].dt.date).size()
bar_chart = px.bar(data, x=data.index, y=data.values)
bar_chart.update_traces(showlegend=False)
bar_chart.update_layout(
    xaxis=dict(
        tickvals=list(data.index), 
    )
)
st.plotly_chart(bar_chart, use_container_width=True)

# Contar quantos testes cada operador realizou
operator_counts = df["operador_id.nome"].value_counts().reset_index()
operator_counts.columns = ["Operador", "Quantidade"]

# Criar o gráfico de pizza
pie_chart = px.pie(
    operator_counts, 
    names="Operador", 
    values="Quantidade", 
    title="Testes realizados por operador",
)

# Exibir no Streamlit
st.plotly_chart(pie_chart, use_container_width=True)

with st.expander(f"BASE DE DADOS - {df.shape[0]} testes"):
    st.dataframe(df)

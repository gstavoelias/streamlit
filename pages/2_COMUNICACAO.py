import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from server import Server

st.set_page_config(
    page_title="Banco de Dados TECSCI",
    page_icon="icon.ico",
    layout="wide"
)

st.title("Dashboard - Teste de Comunicação")
with st.sidebar:
    st.image("logo-dark.png")
    st.write("#")
    st.write("#")



server = Server()
df = server.get_communication_data()
with st.expander(f"BASE DE DADOS - {df.shape[0]} testes"):
    st.dataframe(df)


st.write("## Testes por dia:")
months = df["horario"].dt.strftime('%Y-%m').unique()
selected_month = st.selectbox("Selecione o mês:", months)
df = df[df["horario"].dt.strftime('%Y-%m') == selected_month]

data = df.groupby(df["horario"].dt.date).size()
bar_chart = px.bar(data, x=data.index, y=data.values)
bar_chart.update_traces(showlegend=False)
bar_chart.update_layout(
    xaxis=dict(
        tickvals=list(data.index), 
    )
)
st.plotly_chart(bar_chart, use_container_width=True)

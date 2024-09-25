import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from server import Server

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
with st.expander(f"BASE DE DADOS - {server.df.shape[0]} testes"):
    st.dataframe(server.df)


st.write("## Testes por dia:")
data = server.df.groupby(server.df["horario"].dt.date).size()
bar_chart = px.bar(data, x=data.index, y=data.values)
bar_chart.update_traces(showlegend=False)
bar_chart.update_layout(
    xaxis=dict(
        tickvals=list(data.index), 
    )
)
st.plotly_chart(bar_chart, use_container_width=True)

st.write("## Duração dos testes:")
st.write(f"- Média: {server.df["duracao"].mean():.2f}")
st.write(f"- Máximo: {server.df["duracao"].max():.2f}")
st.write(f"- Mínimo: {server.df["duracao"].min():.2f}")

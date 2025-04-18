import streamlit as st 
from server import Server
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard TECSCI", page_icon="icon.ico", layout="wide")
with st.sidebar:
    st.image("logo-dark.png")


st.title("Relatório de Falhas das TCUs TECSCI")
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.stop()
st.header("Falhas por dia")

api = st.session_state.api
response = api.get_rft()
df = pd.json_normalize(response)

df["horario"] = pd.to_datetime(df["horario"])
data = df.groupby(df["horario"].dt.date).size()
bar_chart = px.bar(data, x=data.index, y=data.values,color_discrete_sequence=px.colors.sequential.Inferno)
bar_chart.update_traces(showlegend=False)
bar_chart.update_layout(xaxis=dict(tickvals=list(data.index)))
st.text(f"TOTAL: {len(df)}")
st.plotly_chart(bar_chart, use_container_width=True, theme="streamlit")

col1, col2 = st.columns(2)

with col1:
    st.header("Falhas por Etapa")
    etapas = df["erro_id.etapa.nome"].value_counts().reset_index()
    etapas.columns = ["Etapa", "Quantidade"]
    etapas_chart = px.pie(etapas, names="Etapa", values="Quantidade", color_discrete_sequence=px.colors.sequential.Inferno)
    st.plotly_chart(etapas_chart, use_container_width=True)

with col2:
    st.header("Falhas por operador")
    operadores = df["operador_id.nome"].value_counts().reset_index()
    operadores.columns = ["Operador", "Falhas"]
    operador_chart = px.bar(operadores, x="Operador", y="Falhas", title="Falhas por Operador", color_discrete_sequence=px.colors.sequential.Inferno)
    st.plotly_chart(operador_chart, use_container_width=True)


st.header("Tipos de Erro por Etapa")
etapas_disponiveis = ["TODOS"] + sorted(df["erro_id.etapa.nome"].dropna().unique().tolist())
etapa_selecionada = st.selectbox("Selecione a Etapa", etapas_disponiveis)

# Aplicar filtro se necessário
if etapa_selecionada != "TODOS":
    df_pizza = df[df["erro_id.etapa.nome"] == etapa_selecionada]
else:
    df_pizza = df

# ⚠️ Gráfico: Tipos de Erro (filtrado)
tipos_erro = df_pizza["erro_id.nome"].value_counts().reset_index()
tipos_erro.columns = ["Erro", "Ocorrências"]
erro_chart = px.pie(tipos_erro, names="Erro", values="Ocorrências", title=None, color_discrete_sequence=px.colors.sequential.Inferno)
st.text(f"TOTAL: {len(df_pizza)}")
st.plotly_chart(erro_chart, use_container_width=True)



with st.expander("Base de Dados", expanded=False):
    st.dataframe(df, use_container_width=True, hide_index=True)
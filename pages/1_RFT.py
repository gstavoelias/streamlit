import streamlit as st 
import pandas as pd
import plotly.express as px
from utils import render_header

# HEADER
render_header("Análise de Falhas")

# CARREGANDO DADOS
api = st.session_state.api
response = api.get_rft()
df = pd.json_normalize(response)

### PLOT DE QNT X DIA
st.header("Falhas por dia")
agrupamento = st.radio("Tipo de agrupamento", options=["Dia", "Semana", "Mês"], horizontal=True)
df["horario"] = pd.to_datetime(df["horario"], format='ISO8601')
if agrupamento == "Dia":
    data = df.groupby(df["horario"].dt.date).size()
elif agrupamento == "Semana":
    data = df.groupby(df["horario"].dt.to_period("W")).size()
elif agrupamento == "Mês":
    data = df.groupby(df["horario"].dt.to_period("M")).size()
data.index = data.index.astype(str)
grafico = px.bar(
    data,
    x=data.index,
    y=data.values,
    color_discrete_sequence=px.colors.sequential.Inferno
)
grafico.update_traces(showlegend=False)
st.text(f"TOTAL: {len(df)}")
st.plotly_chart(grafico, use_container_width=True)


# PLOT DE FALHAS X ETAPAS E FALHAS X OPERADOR
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


# PLOT DE ERROS X ETAPAS
st.header("Tipos de Erro por Etapa")
etapas_disponiveis = ["TODOS"] + sorted(df["erro_id.etapa.nome"].dropna().unique().tolist())
etapa_selecionada = st.selectbox("Selecione a Etapa", etapas_disponiveis)
if etapa_selecionada != "TODOS":
    df_pizza = df[df["erro_id.etapa.nome"] == etapa_selecionada]
else:
    df_pizza = df
tipos_erro = df_pizza["erro_id.nome"].value_counts().reset_index()
tipos_erro.columns = ["Erro", "Ocorrências"]
erro_chart = px.pie(tipos_erro, names="Erro", values="Ocorrências", title=None, color_discrete_sequence=px.colors.sequential.Inferno)
st.text(f"TOTAL: {len(df_pizza)}")
st.plotly_chart(erro_chart, use_container_width=True)


# DATAFRAME COMPLETO
with st.expander("Base de Dados", expanded=False):
    st.dataframe(df, use_container_width=True, hide_index=True)
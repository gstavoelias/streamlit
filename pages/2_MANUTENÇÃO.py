import streamlit as st 
import pandas as pd
import plotly.express as px
from utils import render_header


render_header("Análise de Manutenções")

# LOAD DATA
api = st.session_state.api
response = api.get_manutencao()
df = pd.json_normalize(response)

# PLOT DE QNT X DIA
st.header("Manutenções por dia")
agrupamento = st.radio("Tipo de agrupamento", options=["Dia", "Semana", "Mês"], horizontal=True)
df["horario"] = pd.to_datetime(df["horario"])
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
    color_discrete_sequence=px.colors.sequential.Viridis_r[3:]
)
grafico.update_traces(showlegend=False)
st.text(f"TOTAL: {len(df)}")
st.plotly_chart(grafico, use_container_width=True)


# PLOT DE SOLUCOES X ERROS
st.header("Soluções por Erro:")
df["etapa_erro"] = df["rft.erro_id.etapa.nome"] + " – " + df["rft.erro_id.nome"]
opcoes = df["etapa_erro"].dropna().unique().tolist()
opcoes.sort()
opcoes.insert(0, "TODOS")
selecionado = st.selectbox("Selecione o Tipo de Falha", opcoes)


if selecionado == "TODOS":
    df_filtrado = df
else:
    etapa_selecionada, falha_selecionada = selecionado.split(" – ", 1)
    df_filtrado = df[
        (df["rft.erro_id.etapa.nome"] == etapa_selecionada) &
        (df["rft.erro_id.nome"] == falha_selecionada)
    ]
solucoes = df_filtrado["solucao.nome"].value_counts().reset_index()
solucoes.columns = ["Solução", "Quantidade"]
grafico_solucao = px.pie(solucoes, names="Solução", values="Quantidade", color_discrete_sequence=px.colors.sequential.Viridis_r[3:])
st.text(f"TOTAL: {len(df_filtrado)}")
st.plotly_chart(grafico_solucao, use_container_width=True)


# PLOT DE MANUTENCOES X OPERADORES
st.header("Manutenções por Operador")
por_operador = df["operador_id.nome"].value_counts().reset_index()
por_operador.columns = ["Operador", "Quantidade"]
chart = px.bar(por_operador, x="Operador", y="Quantidade", color_discrete_sequence=px.colors.sequential.Viridis_r[3:])
st.text(f"TOTAL: {len(por_operador)}")
st.plotly_chart(chart, use_container_width=True)


# DATAFRAME COMPLETO
with st.expander("Base de Dados", expanded=False):
    st.dataframe(df, use_container_width=True, hide_index=True)
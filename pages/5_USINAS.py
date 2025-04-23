import streamlit as st
import pandas as pd
import plotly.express as px
from utils import render_header


render_header("Relatório de Usinas")

color_sequence = px.colors.sequential.Agsunset

df = pd.read_excel("alarmes.xlsx", sheet_name="Histórico de alarmes", dtype={"Numero TCU": str, "Ultima comunicação": str})
df["Dia"] = pd.to_datetime(df["Dia"])

# HISTÓRICO DE DATA
data = df.groupby(df["Dia"].dt.date).size()
bar_chart = px.bar(df, x=data.index, y=data.values, title="Histórico de alarmes", labels={"x": "Dia", "y": "Quantidade de Alarmes"}, color_discrete_sequence=color_sequence)
st.plotly_chart(bar_chart)


#FALHAS POR USINA
erros_usina = df["Cidade"].value_counts().reset_index()
erros_usina.columns = ["Usina", "Quantidade"]
pie_chart = px.pie(erros_usina, title="Falhas por Usina", names="Usina", values="Quantidade", color_discrete_sequence=color_sequence)
st.plotly_chart(pie_chart)


# TIPOS DE FALHAS MAIS COMUNS
usinas = ["TODAS"] + sorted(df["Cidade"].fillna("Bebedouro").unique().tolist())
usina = st.selectbox(label="Usina", options=usinas)
df_filtrado = df[df["Cidade"] == usina] if usina != "TODAS" else df

erros = df_filtrado["Tipo de problema"].value_counts().reset_index()
erros.columns = ["Tipo de problema", "Quantidade"]
pie_chart2 = px.pie(erros, title="Tipos de Falha", names="Tipo de problema", values="Quantidade", color_discrete_sequence=color_sequence)
st.plotly_chart(pie_chart2)


st.dataframe(df)
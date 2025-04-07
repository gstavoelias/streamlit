import streamlit as st 
from server import Server
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard TECSCI", page_icon="icon.ico", layout="wide")
with st.sidebar:
    st.image("logo-dark.png")


st.title("Relatório de Falha das TCUs TECSCI")
server = Server("http://127.0.0.1:8087/api/v1.0/")


st.header("Manutenções por dia")
response = server.get_manutencao()
df = pd.json_normalize(response)
df["horario"] = pd.to_datetime(df["horario"])
data = df.groupby(df["horario"].dt.date).size()
bar_chart = px.bar(data, x=data.index, y=data.values,color_discrete_sequence=["#00C853"])
bar_chart.update_traces(showlegend=False)
bar_chart.update_layout(xaxis=dict(tickvals=list(data.index)))
st.plotly_chart(bar_chart, use_container_width=True, theme="streamlit")
st.text(f"TOTAL: {len(df)}")


st.header("Soluções por Erro:")
# Criar coluna combinando etapa + erro
df["etapa_erro"] = df["rft.erro_id.etapa.nome"] + " – " + df["rft.erro_id.nome"]

# Listar opções únicas para o menu
opcoes = df["etapa_erro"].dropna().unique().tolist()
opcoes.sort()
selecionado = st.selectbox("Selecione o Tipo de Falha", opcoes)

# Separar etapa e erro a partir do valor selecionado
etapa_selecionada, falha_selecionada = selecionado.split(" – ", 1)

# Filtrar o DataFrame com base em etapa e erro
df_filtrado = df[
    (df["rft.erro_id.etapa.nome"] == etapa_selecionada) &
    (df["rft.erro_id.nome"] == falha_selecionada)
]

# Agrupar soluções
solucoes = df_filtrado["solucao.nome"].value_counts().reset_index()
solucoes.columns = ["Solução", "Quantidade"]

# Título e gráfico
grafico_solucao = px.pie(solucoes, names="Solução", values="Quantidade", color_discrete_sequence=["#00C853"])
st.plotly_chart(grafico_solucao, use_container_width=True)

st.header("Manutenções por Operador")
por_operador = df["operador_id.nome"].value_counts().reset_index()
por_operador.columns = ["Operador", "Quantidade"]
chart = px.bar(por_operador, x="Operador", y="Quantidade", color_discrete_sequence=["#00C853"])
st.plotly_chart(chart, use_container_width=True)

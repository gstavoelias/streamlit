import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

# CONFIGURA A PÁGINA
st.set_page_config(
    page_title="Banco de Dados TECSCI",
    page_icon="icon.ico",
    layout="wide"
)
st.title("Dashboard - Testes das RAK")
# MENU LATERAL
with st.sidebar:
    st.image("logo-dark.png")
    st.write("#")
    st.write("#")
    # st.write("## Baixar CSV:")
    # st.write("###")
    # download_files = st.download_button("Download", data=convert_df(df), file_name="uploaded_files.csv", mime="text/csv")


# # PEGA OS DADOS DA ENDPOINT E RETORNA DF
# @st.cache_data
# def load_df():
#     data = requests.get("http://192.168.68.117:8087/api/v1.0/teste_rak").json()
#     df = pd.json_normalize(data)
#     df = df[["operador_id", "horario", "offset", "rak_id", "resultado_comunicacao", "resultado_rf", "potencia_minima", "potencia_media", "potencia_maxima"]]
#     df["horario"] = pd.to_datetime(df["horario"], format="mixed")
#     return df


# # CONVERTE O DF PARA DOWNLOAD
# @st.cache_data
# def convert_df(df):
#     return df.to_csv().encode("utf-8")


# # CARREGA O DF
# df = load_df()
# if df is None:
#     st.info("Não há dados disponiveis", icon="i")


# ## PIECHART 
# values = [len(df[df["resultado_rf"] == True]), len(df[df["resultado_rf"] == False])]
# st.write(f"## Testes bem sucedidos:")
# pie_chart = px.pie(names=["OK", "NG"], values=values)
# st.plotly_chart(pie_chart)

# ## LINE CHART
# col1, col2 = st.columns(2)
# with col1:
#     line_chart = px.line(df["potencia_media"])
#     line_chart.add_trace(go.Scatter(
#         x = df.index,
#         y = [df["potencia_media"].mean()] * len(df),
#         name = "MÉDIA",
#         line=dict(dash="dash"),
#     ))
#     st.write("## Potência Média:")
#     st.plotly_chart(line_chart, use_container_width=True)

# ## BAR CHART
# with col2:
#     bar_chart = px.bar(df.groupby(df["horario"].dt.date).size())
#     bar_chart.update_traces(showlegend=False)
#     st.write("## Testes realizados por dia:")
#     st.plotly_chart(bar_chart, use_container_width=True)


# ## BASE DE DADOS
# df['resultado_comunicacao'] = df['resultado_comunicacao'].apply(lambda x: '✅' if x else '❌')
# df['resultado_rf'] = df['resultado_rf'].apply(lambda x: '✅' if x else '❌')
# df['potencia'] = df.apply(lambda row: [row['potencia_minima'], row['potencia_media'], row['potencia_maxima']], axis=1)
# df = df.drop(["potencia_minima", "potencia_media", "potencia_maxima"], axis=1)
# with st.expander("BASE DE DADOS:"):   
#     st.dataframe(df, 
#                  column_config= {
#                   "potencia": st.column_config.LineChartColumn(),
#                  },
#                  hide_index=True)



#TESTE
# df2 = pd.read_csv("./BURNIN.csv")

# tensao_painel_cols = [col for col in df2.columns if 'tensao_painel' in col]
# tensao_painel_cols.reverse()
# df2['TENSÃO PAINEL'] = df2.apply(lambda row: [row[col] for col in tensao_painel_cols], axis=1)
# df2 = df2.drop(tensao_painel_cols, axis=1)

# tensao_motor_cols = [col for col in df2.columns if 'tensao_motor' in col]
# tensao_motor_cols.reverse()
# df2['TENSÃO MOTOR'] = df2.apply(lambda row: [row[col] for col in tensao_motor_cols], axis=1)
# df2 = df2.drop(tensao_motor_cols, axis=1)

# corrente_motor_cols = [col for col in df2.columns if 'corrente_motor' in col]
# corrente_motor_cols.reverse()
# df2['CORRENTE MOTOR'] = df2.apply(lambda row: [row[col] for col in corrente_motor_cols], axis=1)
# df2 = df2.drop(corrente_motor_cols, axis=1)

# estado_bateria_cols = [col for col in df2.columns if 'estado_bateria' in col]
# estado_bateria_cols.reverse()
# df2['ESTADO BATERIA'] = df2.apply(lambda row: [row[col] for col in estado_bateria_cols], axis=1)
# df2 = df2.drop(estado_bateria_cols, axis=1)

# temperatura_cols = [col for col in df2.columns if 'temperatura' in col]
# temperatura_cols.reverse()
# df2['TEMPERATURA PAINEL'] = df2.apply(lambda row: [row[col] for col in temperatura_cols], axis=1)
# df2 = df2.drop(temperatura_cols, axis=1)

# posicao_angular_cols = [col for col in df2.columns if 'posicao_angular' in col]
# posicao_angular_cols.reverse()
# df2['POSIÇÃO ANGULAR'] = df2.apply(lambda row: [row[col] for col in posicao_angular_cols], axis=1)
# df2 = df2.drop(posicao_angular_cols, axis=1)

# with st.expander("EXEMPLO BURNIN"):
#     st.dataframe(df2,
#                  column_config={
#                      "TENSÃO PAINEL": st.column_config.LineChartColumn(),
#                      "TENSÃO MOTOR": st.column_config.LineChartColumn(),
#                      "CORRENTE MOTOR": st.column_config.LineChartColumn(),
#                      "ESTADO BATERIA": st.column_config.LineChartColumn(),
#                      "TEMPERATURA PAINEL": st.column_config.LineChartColumn(),
#                      "POSIÇÃO ANGULAR": st.column_config.LineChartColumn(),
#                  },
#                  hide_index= True)


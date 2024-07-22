import streamlit as st
import pandas as pd
import sqlite3
import io
import plotly.express as px
import plotly.graph_objects as go


# Configurações da página
st.set_page_config(
    page_title="Banco de Dados",
    page_icon="icon.ico",
    layout="wide"
)
st.title("Banco de Dados das RAKs")


# Configuração do banco de dados SQLite
connection = sqlite3.connect('uploaded_files.db')
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS files
             (name TEXT, data BLOB)''')
connection.commit()


# Função para carregar arquivos do banco de dados e compilar eles num dataframe
@st.cache_data
def load_df():
    cursor.execute("SELECT name, data FROM files")
    files = cursor.fetchall()
    dfs = [pd.read_csv(io.BytesIO(data)) for name, data in files]
    df = pd.concat(dfs, ignore_index=True)
    df = df.drop_duplicates(subset="DEVEUI", keep="last")
    df = df.dropna(subset=["RESULTADO RF"])
    df = df.reset_index(drop=True)
    df["HORARIO"] = pd.to_datetime(df["HORARIO"], format='%Y-%m-%d_%H-%M-%S')
    return df


# Função que converte o dataframe num csv para download
@st.cache_data
def convert_df(df):
    return df.to_csv().encode("utf-8")


# Função para salvar arquivo no banco de dados
def save_file(file):
    cursor.execute("INSERT INTO files (name, data) VALUES (?, ?)", (file.name, file.getvalue()))
    connection.commit()


# Função para validar o arquivo CSV upado, validação tá sendo só verificar se tem a tabela USUARIO
def validate_csv(file):
    try:
        df = pd.read_csv(file)
        if 'USUARIO' in df.columns:
            return True
        else:
            return False
    except Exception:
        return False
    

# Carregar os arquivos armazenados
df = load_df()
if df is None:
    st.info("Não há dados disponiveis", icon="i")

# Widget do Menu Lateral, contém o file uploader e a opção de baixar arquivos
with st.sidebar:
    st.image("logo-dark.png")
    st.write("#")
    st.write("#")
    st.write("## Baixar CSV:")
    st.write("###")
    download_files = st.download_button("Download", data=convert_df(df), file_name="uploaded_files.csv", mime="text/csv")
    st.write("###")
    st.write("## Enviar CSV:")
    uploaded_file = st.file_uploader(label="hidden", label_visibility="hidden", type="csv")
    if uploaded_file is not None:
        if validate_csv(uploaded_file):
            save_file(uploaded_file)
            st.success("Arquivo carregado com sucesso!")
        else:
            st.error("O arquivo CSV não está na formatação correta.")



## Exibição do piechart com a quantidade de RAKs testadas
values = [len(df[df["RESULTADO RF"] == "OK"]), len(df[df["RESULTADO RF"] == "NG"])]
st.write(f"## RAKs Testadas: {len(df["DEVEUI"])}")
pie_chart = px.pie(names=["OK", "NG"], values=values)
st.plotly_chart(pie_chart)

col1, col2 = st.columns(2)

## Coluna 1: Exibição do gráfico de linha da potência média
with col1:
    line_chart = px.line(df["POTENCIA MEDIA"])
    line_chart.add_trace(go.Scatter(
        x = df.index,
        y = [df["POTENCIA MEDIA"].mean()] * len(df),
        name = "MÉDIA",
        line=dict(dash="dash"),
    ))
    st.write("## POTENCIA MÉDIA:")
    st.plotly_chart(line_chart, use_container_width=True)

## Coluna 2: Exibição do gráfico de barra de RAKs Testadas/Dia
with col2:
    bar_chart = px.bar(df.groupby(df["HORARIO"].dt.date).size())
    bar_chart.update_traces(showlegend=False)
    st.write("## Testes realizados por dia:")
    st.plotly_chart(bar_chart, use_container_width=True)


## Exibição da Base de Dados
df['RESULTADO COMUNICACAO'] = df['RESULTADO RF'].apply(lambda x: '✅' if x == 'OK' else '❌')
df['RESULTADO RF'] = df['RESULTADO RF'].apply(lambda x: '✅' if x == 'OK' else '❌')
df['POTENCIA'] = df.apply(lambda row: [row['POTENCIA MINIMA'], row['POTENCIA MEDIA'], row['POTENCIA MAXIMA']], axis=1)
df = df.drop(["POTENCIA MINIMA", "POTENCIA MAXIMA", "POTENCIA MEDIA", "SAMPLES"], axis=1)

with st.expander("BASE DE DADOS:"):   
    st.dataframe(df, 
                 column_config= {
                  "POTENCIA": st.column_config.LineChartColumn("POTÊNCIA"),
                 },
                 hide_index=True)


# Fechar a conexão com o banco de dados
connection.close()
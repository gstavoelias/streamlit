import streamlit as st
import pandas as pd
import sqlite3
import io
import plotly.express as px
import plotly.graph_objects as go

# Configuração do banco de dados SQLite
connection = sqlite3.connect('uploaded_files.db')
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS files
             (name TEXT, data BLOB)''')
connection.commit()

# Função para salvar arquivo no banco de dados
def save_file(file):
    cursor.execute("INSERT INTO files (name, data) VALUES (?, ?)", (file.name, file.getvalue()))
    connection.commit()

# Função para carregar arquivos do banco de dados
def load_files():
    cursor.execute("SELECT name, data FROM files")
    files = cursor.fetchall()
    return files


# Função para validar o arquivo CSV upado
def validate_csv(file):
    try:
        df = pd.read_csv(file)
        if 'USUARIO' in df.columns:
            return True
        else:
            return False
    except Exception:
        return False


# Interface do Usuário
st.set_page_config(layout="wide")
st.title("Banco de dados das RAKs")
st.write("## Envio de dados:")
uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")

if uploaded_file is not None:
    if validate_csv(uploaded_file):
        save_file(uploaded_file)
        st.success("Arquivo carregado com sucesso!")
    else:
        st.error("O arquivo CSV não está na formatação correta.")


# Carregar os arquivos armazenados
files = load_files()
dfs = [pd.read_csv(io.BytesIO(data)) for name, data in files]
df = pd.concat(dfs, ignore_index=True)
df = df.drop_duplicates(subset="DEVEUI",keep="last")
df = df.dropna(subset="RESULTADO RF")
df.reindex()
df["HORARIO"] = pd.to_datetime(df["HORARIO"], format='%Y-%m-%d_%H-%M-%S')



## EXIBIR O PIECHART DE RAKS TESTADAS
values = [len(df[df["RESULTADO RF"] == "OK"]), len(df[df["RESULTADO RF"] == "NG"])]
st.write(f"## RAKs Testadas: {len(df["DEVEUI"])}")
pie_chart = px.pie(names=["OK", "NG"], values=values)
st.plotly_chart(pie_chart)

col1, col2 = st.columns(2)

## POTENCIA MÉDIA
with col1:
    line_chart = px.line(df["POTENCIA MEDIA"])
    line_chart.add_trace(go.Scatter(
        x = df.index,
        y = [df["POTENCIA MEDIA"].mean()] * len(df),
        name = "MÉDIA",
        line=dict(dash="dash"),
    ))
    st.write("## POTENCIA MÉDIA:")
    st.plotly_chart(line_chart)

## EXIBIR A QUANTIDADE DE RAKS TESTADAS POR DIA
with col2:
    bar_chart = px.bar(df.groupby(df["HORARIO"].dt.date).size())
    bar_chart.update_traces(showlegend=False)
    st.write("## Testes realizados por dia:")
    st.plotly_chart(bar_chart)


## EXIBIR A DB
st.write("## Base de Dados:")
st.write(df)


    
# Fechar a conexão com o banco de dados
connection.close()
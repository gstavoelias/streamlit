import streamlit as st
import pandas as pd
import sqlite3
import io

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
st.title("Upload e Visualização de Arquivos CSV")
uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")

if uploaded_file is not None:
    if validate_csv(uploaded_file):
        save_file(uploaded_file)
        st.success("Arquivo carregado com sucesso!")
    else:
        st.error("O arquivo CSV não está na formatação correta.")


st.write("## Base de Dados")
# Carregar e exibir os arquivos armazenados
files = load_files()
dfs = [pd.read_csv(io.BytesIO(data)) for name, data in files]
df = pd.concat(dfs, ignore_index=True)
st.write(df)

x = df["DEVEUI"].dropna().unique()
    
st.write(f"### QUANTIDADE DE RAKS TESTADAS: {len(x)}")
# Fechar a conexão com o banco de dados
connection.close()
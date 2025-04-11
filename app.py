import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
from server import Server  # Certifique-se de que o Server possui os métodos necessários

# Configuração da página
st.set_page_config(page_title="Dashboard TECSCI", page_icon="icon.ico", layout="wide")

# Inicializa o estado
if "selected_test_type" not in st.session_state:
    st.session_state.selected_test_type = None
if "selected_period" not in st.session_state:
    st.session_state.selected_period = "SEMANA"

# Função para calcular a data de início com base no período
def get_date_filter(period):
    hoje = datetime.today()
    if period == "SEMANA":
        start = hoje - timedelta(days=(hoje.weekday() + 1))
        return f"datetime >= '{start}'"
    elif period == "ÚLTIMA SEMANA":
        fim_ultima = hoje - timedelta(days=(hoje.weekday() + 1))
        inicio_ultima = fim_ultima - timedelta(days=7)
        return f"datetime >= '{inicio_ultima}' and datetime < '{fim_ultima}'"
    elif period == "MÊS":
        start = hoje.replace(day=1)
        return f"datetime >= '{start}'"
    elif period == "SEMESTRE":
        primeiro_mes = 1 if hoje.month <= 6 else 7
        start = hoje.replace(month=primeiro_mes, day=1)
        return f"datetime >= '{start}'"
    elif period == "ANO":
        start = hoje.replace(month=1, day=1)
        return f"datetime >= '{start}'"
    else:  # TOTAL
        return None



# Sidebar
with st.sidebar:
    st.image("logo-dark.png")
    
    test_type = st.selectbox("Selecione o tipo de teste", ["", "Burn In", "Teste de Comunicação", "Teste de Potência"])
    st.session_state.selected_test_type = test_type

    st.session_state.selected_period = st.selectbox(
        "Selecione o intervalo de tempo", ["ÚLTIMA SEMANA", "SEMANA", "MÊS", "SEMESTRE", "ANO", "TOTAL"],
        index=["ÚLTIMA SEMANA", "SEMANA", "MÊS", "SEMESTRE", "ANO", "TOTAL"].index(st.session_state.selected_period)
    )

    empresa_selecionada = st.selectbox(
        "Selecione a empresa", 
        ["TODAS", "TECSCI", "Enterplak", "Infinity"]
    )

# Cabeçalho principal
if not st.session_state.selected_test_type:
    st.title("Dashboard TECSCI")
    st.info("Selecione um tipo de teste na barra lateral para começar.")
else:
    st.title(f"Dashboard - {st.session_state.selected_test_type}")

    # Inicializa o servidor
    server = Server()

    # Busca os dados
    filtro = get_date_filter(st.session_state.selected_period)
    if st.session_state.selected_test_type == "Burn In":
        df = server.get_burnin_data(filtro)
    elif st.session_state.selected_test_type == "Teste de Comunicação":
        df = server.get_communication_data(filtro)
    elif st.session_state.selected_test_type == "Teste de Potência":
        df = server.get_power_data(filtro)
    else:
        df = None

    if empresa_selecionada != "TODAS":
            df = df[df["operador_id.empresa.nome"] == empresa_selecionada]

    # Verifica erro na requisição
    if server.excecao is not None:
        st.error(f"Houve um erro: {server.excecao}")

    elif df is not None and not df.empty:
        # Gráfico de barras por dia
        st.subheader("Testes realizados por dia")
        data = df.groupby(df["horario"].dt.date).size()
        bar_chart = px.bar(data, x=data.index, y=data.values)
        bar_chart.update_traces(showlegend=False)
        bar_chart.update_layout(xaxis=dict(tickvals=list(data.index)))
        st.plotly_chart(bar_chart, use_container_width=True)
        st.text(f"TOTAL: {len(df)}")

        # Gráfico de pizza por operador
        st.subheader("Distribuição por Operador")
        operator_counts = df["operador_id.nome"].value_counts().reset_index()
        operator_counts.columns = ["Operador", "Quantidade"]
        pie_chart = px.pie(operator_counts, names="Operador", values="Quantidade")
        st.plotly_chart(pie_chart, use_container_width=True)

        # Exibe DataFrame completo
        with st.expander(f"BASE DE DADOS - {df.shape[0]} registros"):
            st.dataframe(df, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado para o período selecionado.")

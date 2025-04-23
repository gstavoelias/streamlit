import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
from utils import Server, render_header

if "api" not in st.session_state:
    st.session_state.api = Server()
api = st.session_state.api 

render_header("Dashboard TECSCI", is_main_page=True)
# Inicializa estado de seleção
if "selected_test_type" not in st.session_state:
    st.session_state.selected_test_type = None
if "selected_period" not in st.session_state:
    st.session_state.selected_period = "SEMANA"

# Função de filtro de data
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
    else:
        return None

# Sidebar
with st.sidebar:
    test_type = st.selectbox("Selecione o tipo de teste", ["Burn In", "Teste de Comunicação", "Teste de Potência"],
                            index=None, placeholder="Selecione o tipo de teste",
                            label_visibility="collapsed")
    st.session_state.selected_test_type = test_type

    st.session_state.selected_period = st.selectbox(
        label="Selecione o intervalo de tempo", label_visibility="collapsed",
        options=["ÚLTIMA SEMANA", "SEMANA", "MÊS", "SEMESTRE", "ANO", "TOTAL"],
        index=None, placeholder="Selecione o intervalo de tempo",
    )
    empresa_selecionada = st.selectbox(
        label="Selecione a empresa", label_visibility="collapsed", 
        options=["TODAS", "TECSCI", "Enterplak", "Infinity"],
        index=None, placeholder="Selecione a empresa"
    )

# Conteúdo
if not st.session_state.selected_test_type or not st.session_state.selected_period:
    st.info("Selecione um tipo de teste na barra lateral para começar.")
else:
    st.title(f"Dashboard - {st.session_state.selected_test_type}")

    filtro = get_date_filter(st.session_state.selected_period)
    df = None

    if st.session_state.selected_test_type == "Burn In":
        df = api.get_burnin_data(filtro)
    elif st.session_state.selected_test_type == "Teste de Comunicação":
        df = api.get_communication_data(filtro)
    elif st.session_state.selected_test_type == "Teste de Potência":
        df = api.get_power_data(filtro)

    if empresa_selecionada != "TODAS" and df is not None:
        df = df[df["operador_id.empresa.nome"] == empresa_selecionada]

    if api.excecao is not None:
        st.error(f"Houve um erro: {api.excecao}")
    elif df is not None and not df.empty:
        st.subheader("Testes realizados por dia")
        data = df.groupby(df["horario"].dt.date).size()
        bar_chart = px.bar(data, x=data.index, y=data.values)
        bar_chart.update_traces(showlegend=False)
        bar_chart.update_layout(xaxis=dict(tickvals=list(data.index)))
        st.plotly_chart(bar_chart, use_container_width=True)
        st.text(f"TOTAL: {len(df)}")

        st.subheader("Distribuição por Operador")
        operator_counts = df["operador_id.nome"].value_counts().reset_index()
        operator_counts.columns = ["Operador", "Quantidade"]
        pie_chart = px.pie(operator_counts, names="Operador", values="Quantidade")
        st.plotly_chart(pie_chart, use_container_width=True)

        with st.expander(f"BASE DE DADOS - {df.shape[0]} registros"):
            st.dataframe(df, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado para o período selecionado.")

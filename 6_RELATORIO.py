import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
from utils import render_header
import pandas as pd
import pytz
from streamlit_extras.metric_cards import style_metric_cards


api = st.session_state.api 

render_header("Burn In - Ano Completo")

@st.cache_data(show_spinner=False)
def fetch_burnin_ano():
    start = datetime.today().replace(month=1, day=1)
    filtro = f"datetime >= '{start}'"
    return api.get_burnin_data(filtro)

# Dados fixos
df = fetch_burnin_ano()

# Garantir timezone-aware
df["horario"] = pd.to_datetime(df["horario"])
agora = datetime.now(pytz.UTC)

# Semana passada
inicio_semana_passada = (agora - timedelta(days=agora.weekday() + 7)).replace(hour=0, minute=0, second=0, microsecond=0)
fim_semana_passada = inicio_semana_passada + timedelta(days=6, hours=23, minutes=59, seconds=59)
semana_passada_total = df[(df["horario"] >= inicio_semana_passada) & (df["horario"] <= fim_semana_passada)].shape[0]

# Mês atual
inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
mes_total = df[df["horario"] >= inicio_mes].shape[0]

# Ano atual
inicio_ano = agora.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
ano_total = df[df["horario"] >= inicio_ano].shape[0]

# KPIs
col1, col2, col3 = st.columns(3, gap='small')
with col1:
    st.metric(label="Produção Semanal", value=f"{semana_passada_total}")
with col2:
    st.metric(label="Produção Mensal", value=f"{mes_total}")
with col3:
    st.metric(label="Produção Anual", value=f"{ano_total}")


style_metric_cards(background_color="#262730", border_left_color=px.colors.sequential.Blues_r[1], border_color="#0E1117")

if api.excecao is not None:
    st.error(f"Houve um erro: {api.excecao}")
elif df is not None and not df.empty:
    st.subheader("Testes realizados por mês")
    df["horario"] = pd.to_datetime(df["horario"])


    m_data = df[df["horario"] >= datetime.today().replace(day=1).astimezone(pytz.UTC)].groupby(df["horario"].dt.date).size()
    m_data.index = m_data.index.astype(str)
    m_chart = px.bar(m_data, x=m_data.index, y=m_data.values, color_discrete_sequence=px.colors.sequential.Blues_r[1:])
    with st.container(border=True):
        st.plotly_chart(m_chart, use_container_width=True)


    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            data = df.groupby(df["horario"].dt.to_period("M")).size()
            data.index = data.index.astype(str)
            percentual = round(data.pct_change() * 100, 2)
            labels = percentual.map(lambda p: (
                f"{p:.1f}% 🟢" if p > 0 else
                f"{p:.1f}% 🔴" if p < 0 else
                f"{p:.1f}% ⚪" if p == 0 else
                ""
            )).tolist()

            bar_chart = px.bar(data, x=data.index, y=data.values, text=labels, color_discrete_sequence=px.colors.sequential.Blues_r[1:])
            bar_chart.update_traces(showlegend=False, textposition="outside")
            bar_chart.update_layout(xaxis=dict(tickvals=list(data.index)))
            st.text(f"TOTAL: {len(df)}")
            st.plotly_chart(bar_chart, use_container_width=True)

    with col2:
        with st.container(border=True):
            data = df[df["horario"] >= datetime.today().replace(day=1).astimezone(pytz.UTC)].groupby(df["horario"].dt.to_period("W")).size()
            data.index = data.index.astype(str)
            percentual = round(data.pct_change() * 100, 2)
            labels = percentual.map(lambda p: (
                f"{p:.1f}% 🟢" if p > 0 else
                f"{p:.1f}% 🔴" if p < 0 else
                f"{p:.1f}% ⚪" if p == 0 else
                ""
            )).tolist()

            bar_chart = px.line(data, x=data.index, y=data.values, text=labels, color_discrete_sequence=px.colors.sequential.Blues_r[1:])
            # bar_chart.update_traces(showlegend=False, textposition="outside")
            bar_chart.update_layout(xaxis=dict(tickvals=list(data.index)))
            st.text(f"TOTAL: {len(df)}")
            st.plotly_chart(bar_chart, use_container_width=True)

    with st.expander("📊 Estatísticas", expanded=False):
        st.markdown(f"- **Total de TCUs:** `{int(data.sum())}`")
        st.markdown(f"- **Média por mês:** `{data.mean():.2f}`")
        st.markdown(f"- **Mediana:** `{data.median():.2f}`")
        st.markdown(f"- **Desvio padrão:** `{data.std():.2f}`")
        st.markdown(f"- **Máximo:** `{data.max()} ({data.idxmax()})`")
        st.markdown(f"- **Mínimo:** `{data.min()} ({data.idxmin()})`")

    st.subheader("Distribuição por Operador")
    operator_counts = df["operador_id.nome"].value_counts().reset_index()
    operator_counts.columns = ["Operador", "Quantidade"]
    pie_chart = px.pie(operator_counts, names="Operador", values="Quantidade", color_discrete_sequence=px.colors.sequential.Blues_r[1:])
    st.plotly_chart(pie_chart, use_container_width=True)

    with st.expander(f"BASE DE DADOS - {df.shape[0]} registros"):
        st.dataframe(df, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado para o período selecionado.")

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import render_header

def prepare_df(df, label):
    if df.empty:
        return pd.DataFrame(columns=["Task", "Start", "End", "Detalhe"])

    if "horario" in df.columns:
        df = df.sort_values("horario")
        start = pd.to_datetime(df["horario"], errors='coerce')
    elif "datetime" in df.columns:
        df = df.sort_values("datetime")
        start = pd.to_datetime(df["datetime"], errors='coerce')
    else:
        start = pd.to_datetime(df.iloc[:, 0], errors='coerce')

    # >>>> AQUI entra o ajuste do horário <<<<
    if label in ["RFT", "Manutenção"]:
        # Identifica quem é exatamente meia-noite
        mask_midnight = start.dt.time == pd.Timestamp("00:00:00").time()
        # Atualiza para 17:00
        start.loc[mask_midnight] = start.loc[mask_midnight] + pd.Timedelta(hours=17)

    tasks = [label] * len(start)

    # Decide se vai usar duracao/duration
    if "duracao" in df.columns:
        duracao = df["duracao"]
    elif "duration" in df.columns:
        duracao = df["duration"]
    else:
        duracao = None

    if duracao is not None:
        if label in ["RFT", "Manutenção"]:
            end = start + pd.to_timedelta(duracao.fillna(30), unit="m")
        else:
            end = start + pd.to_timedelta(duracao.fillna(1800), unit="s")
    else:
        end = start + pd.Timedelta(minutes=30)

    detalhes = ["-"] * len(start)

    return pd.DataFrame({
        "Task": tasks,
        "Start": start,
        "End": end,
        "Detalhe": detalhes
    })


render_header("Rastrear TCU")
api = st.session_state.api

st.header("Teste de Potência")
controladora_id = st.text_input("Número de série", max_chars=13)
filter_dict = {"filter": f"controladora_id = '{controladora_id}'"}
filter_query = f"controladora_id = '{controladora_id}'"

if st.button("Buscar", type="primary"):
    try:
        # --- Busca de dados ---
        df_power = api.get_power_data(filter=filter_query)
        df_comm = api.get_communication_data(filter=filter_query)
        df_burnin = api.get_burnin_data(filter=filter_query)
        df_rft = pd.json_normalize(api._get_request("rft", params=filter_dict))
        df_manutencao = pd.json_normalize(api._get_request("manutencao", params=filter_dict))

        # --- Monta o gantt_df ---
        gantt_dfs = [
            prepare_df(df_power, "Teste de Potência"),
            prepare_df(df_comm, "Comunicação"),
            prepare_df(df_burnin, "Burn-in"),
            prepare_df(df_rft, "RFT"),
            prepare_df(df_manutencao, "Manutenção")
        ]
        gantt_df = pd.concat(gantt_dfs, ignore_index=True)

        if gantt_df.empty:
            st.warning("Nenhum dado encontrado para este número de série.")
            st.stop()

        # --- Linha do Tempo Detalhada com Expanders ---
        with st.container(border=True):
            st.subheader("Linha do Tempo Detalhada")

            task_to_df = {
                "Teste de Potência": df_power,
                "Comunicação": df_comm,
                "Burn-in": df_burnin,
                "RFT": df_rft,
                "Manutenção": df_manutencao
            }

            for index, row in gantt_df.sort_values("Start").iterrows():
                with st.expander(f"{row['Task']} - {row['Start']:%d/%m/%Y %H:%M}"):
                    st.write(f"**Início:** {row['Start']:%d/%m/%Y %H:%M}")
                    st.write(f"**Fim:** {row['End']:%d/%m/%Y %H:%M}")
                    st.write(f"**Detalhes:** {row['Detalhe']}")

                    df_evento = task_to_df.get(row["Task"])
                    if df_evento is not None and not df_evento.empty:
                        st.dataframe(df_evento, use_container_width=True)
                    else:
                        st.info("Nenhum dado disponível para este evento.")

        # --- Gantt Chart ---
        with st.container(border=True):
            st.subheader("Gantt Chart")
            fig = px.timeline(
                gantt_df,
                x_start="Start",
                x_end="End",
                y="Task",
                color="Task",
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig.update_xaxes(showgrid=True)
            fig.update_yaxes(showgrid=True)
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao buscar ou processar dados: {e}")

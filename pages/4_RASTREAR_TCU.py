import streamlit as st
from utils import render_header
import pandas as pd

render_header("Rastrear TCU")
api = st.session_state.api


st.header("Teste de Potência")
controladora_id = st.text_input("Número de série", max_chars=13)
filter = {"filter": f"controladora_id = '{controladora_id}'"}
filter_2 = f"controladora_id = '{controladora_id}'"
if st.button("Buscar", type="primary"):
    df = api.get_power_data(filter=filter_2)
    st.dataframe(df)

    df2 = api.get_communication_data(filter=filter_2)
    st.dataframe(df2)

    df3 = api.get_burnin_data(filter=filter_2)
    st.dataframe(df3)

    rft = api._get_request("rft", params=filter)
    df4 = pd.json_normalize(rft)
    st.dataframe(df4)

    manutencao = api._get_request("manutencao", params=filter)
    df5 = pd.json_normalize(manutencao)
    st.dataframe(df5)

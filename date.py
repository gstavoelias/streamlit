import streamlit as st

data_selecionada_rft = st.date_input("Data", format="DD/MM/YYYY", key="data_rft")
if st.button("enviar"):
    print(data_selecionada_rft.isoformat())
    st.write(data_selecionada_rft.isoformat())
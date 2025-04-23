import streamlit as st
from utils import render_header, render_request_response, load_data


render_header("Adição de Dados")
# LOAD DATA
api = st.session_state.api

# SELECIONAR TIPO DE DADO
tipos_dado = ["RFT + MANUTENÇÃO", "RFT", "MANUTENÇÃO", "ERRO" , "SOLUÇÃO", "MATERIAIS", "PERDAS"]
option = st.selectbox("Tipo de dado", 
                    index = None,
                    placeholder="Selecionar tipo",
                    options=tipos_dado)
st.divider()

# RFT
if option == "RFT + MANUTENÇÃO":
    erros = load_data("erros", api.get_erro)
    erro_map = {f"{e['etapa']} - {e['nome']}": e["id"] for e in erros}

    operadores = load_data("operadores", api.get_operators)
    operador_map = {o["nome"]: o["id"] for o in operadores}

    solucoes = load_data("solucoes", api.get_solucao)
    solucao_map = {s["nome"]: s["id"] for s in solucoes}

    # Campos RFT
    serial_number = st.text_input("Número de série da TCU", max_chars=13)
    operador_selecionado = st.selectbox("Operador", sorted(operador_map.keys()), index=None, placeholder="Selecionar operador")
    erro_selecionado = st.selectbox("Erro", sorted(erro_map.keys()), index=None, placeholder="Selecionar erro")
    descricao_rft = st.text_input("Descrição do RFT", max_chars=150)
    data_rft = st.date_input("Data do RFT", format="DD/MM/YYYY", key="data_rft_man")

    # Campos MANUTENÇÃO
    solucao_selecionada = st.selectbox("Solução", sorted(solucao_map.keys()), index=None, placeholder="Selecionar solução")
    descricao_solucao = st.text_input("Descrição da Solução", max_chars=150)
    duracao = st.text_input("Duração (min)")
    data_man = st.date_input("Data da Manutenção", format="DD/MM/YYYY", key="data_manutencao_man")

    if st.button("ENVIAR", type="primary", key="post_rft_manutencao"):
        # 1. Envia o RFT
        response_rft = api.post_rft(
            serial_number,
            operador_map[operador_selecionado],
            erro_map[erro_selecionado],
            descricao_rft,
            data_rft.isoformat()
        )
        render_request_response(response_rft)

        # 2. Se sucesso no RFT, envia MANUTENÇÃO com último ID
        if response_rft.status_code == 201:
            rfts = api.get_rft()  # recarrega lista pra pegar o novo
            if not rfts:
                st.error("Não foi possível localizar o RFT recém-criado.")
            else:
                last_rft = rfts[-1]
                try:
                    response_man = api.post_manutencao(
                        operador_map[operador_selecionado],
                        last_rft["id"],
                        solucao_map[solucao_selecionada],
                        descricao_solucao,
                        data_man.isoformat(),
                        float(duracao)
                    )
                    render_request_response(response_man)
                except ValueError:
                    st.warning("A duração precisa ser um número válido.")

elif option == "RFT":
    erros = load_data("erros", api.get_erro)
    erro_map = {f"{e['etapa']} - {e['nome']}": e["id"] for e in erros}

    operadores = load_data("operadores", api.get_operators)
    operador_map = {o["nome"]: o["id"] for o in operadores}


    solucoes = load_data("solucoes", api.get_solucao)
    solucao_map = {s["nome"]: s["id"] for s in solucoes}




    serial_number = st.text_input("Número de série da TCU", max_chars=13)
    operador_selecionado = st.selectbox("Operador", sorted(operador_map.keys()),
                                        index=None, placeholder="Selecionar operador")
    erro_selecionado = st.selectbox("Erro", sorted(erro_map.keys()), help="Não encontrou o erro? Adicione abaixo.",
                                    index=None, placeholder="Selecionar erro")
    descricao = st.text_input("Descrição", max_chars=150)
    data_selecionada_rft = st.date_input("Data", format="DD/MM/YYYY", key="data_rft")
    if st.button("ENVIAR", type="primary", key="post_rft"):
        response = api.post_rft(
            serial_number,
            operador_map[operador_selecionado],
            erro_map[erro_selecionado],
            descricao,
            data_selecionada_rft.isoformat()
        )
        render_request_response(response)

# ERRO
elif option == "ERRO":
    etapas = load_data("etapas", api.get_etapa)
    etapas_map = {e["nome"]: e["id"] for e in etapas}


    etapa_selecionada = st.selectbox("Etapa", sorted(etapas_map.keys()))
    erro_nome = st.text_input("Nome do Erro")
    if st.button("ENVIAR", type="primary", key="post_erro"):
        response = api.post_erro(etapas_map[etapa_selecionada], erro_nome)
        render_request_response(response)

# MANUTENÇÃO
elif option == "MANUTENÇÃO":
    rfts = load_data("rfts", api.get_rft)
    rft_map = {
    f"{r['controladora_id']} - {r['erro_id']['nome']} - {r['horario'].split('T')[0]}": r["id"]
    for r in rfts
}
    
    
    operadores = load_data("operadores", api.get_operators)
    operador_map = {o["nome"]: o["id"] for o in operadores}


    rft_selecionado = st.selectbox("RFT", sorted(rft_map.keys()), index=None, placeholder="Selecionar RFT")
    tecnico_selecionado = st.selectbox("Técnico", sorted(operador_map.keys()), index=None, placeholder="Selecionar Técnico")
    solucao_selecionada = st.selectbox("Solução", sorted(solucao_map.keys()), index=None, placeholder="Selecionar Solução")
    descricao_sol = st.text_input("Descrição da Solução:", max_chars=150)
    duracao = st.text_input("Duração (min)")
    data_selecionada_man = st.date_input("Data", format="DD/MM/YYYY", key="data_manutencao")

    if st.button("ENVIAR", type="primary", key="post_manutencao"):
        try:
            response = api.post_manutencao(
                operador_map[tecnico_selecionado],
                rft_map[rft_selecionado],
                solucao_map[solucao_selecionada],
                descricao_sol,
                data_selecionada_man.isoformat(),
                float(duracao)
            )
            render_request_response(response)
        except ValueError:
            st.warning("A duração precisa ser um número válido.")

# SOLUÇÃO
elif option == "SOLUÇÃO":
    sol_nome = st.text_input("Nome da Solução")
    if st.button("ENVIAR", type="primary", key="post_solucao"):
        response = api.post_solucao(sol_nome)
        render_request_response(response)


elif option == "MATERIAIS":
    id = st.text_input("Código")
    nome  = st.text_input("Nome")
    if st.button("ENVIAR", type="primary", key="post_material"):
        response = api.post_material(id, nome)
        render_request_response(response)

elif option == "PERDAS":
    materiais = load_data("materiais", api.get_materials)
    materials_map = {
    f"{m['id']} - {m['nome']}": m["id"] for m in materiais
}

    manutencoes = load_data("manutencoes", api.get_manutencao)



    manutencoes_map = {
        f"{m['rft']['controladora_id']} - {m['solucao']['nome']} - {m['horario'].split('T')[0]}": m["id"]
        for m in manutencoes
    }

    material_selecionado = st.selectbox("Material", options=sorted(materials_map.keys()))
    manutencao_selecionada = st.selectbox("Manutenção", options=sorted(manutencoes_map.keys()))
    quantidade = st.text_input("Quantidade")
    if st.button("ENVIAR", type="primary", key="post_perdas"):
        try:
            response = api.post_perdas(materials_map[material_selecionado], manutencoes_map[manutencao_selecionada], int(quantidade))
            render_request_response(response)
        except ValueError:
            st.warning("A quantidade precisa ser um número válido.")

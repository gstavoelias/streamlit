import requests
import pandas as pd


class Server:
    def __init__(self, server_url="https://ppc.tecsci.com.br/api/v1.0"):
        self.server_url = server_url
        self.token = None
        self.response = None
        self.excecao = None
        self.login()



    def login(self):
        try:
            response = requests.post(
                self.server_url + "/auth/login",
                headers={'Content-Type': 'application/json'}, 
                json={'username': 'gustavo.elias', 'password': '12345678'}
            )

            # Armazena status e texto da resposta para debugging
            self.response = response.text

            if response.status_code != 200:
                self.excecao = f"Erro {response.status_code} - {response.reason}"
                return
            
            self.token = response.json().get("access_token")

        except Exception as e:
            self.excecao = e.args
    
    def _get_request(self, endpoint, params=None):
        return requests.get(self.server_url + endpoint, 
                            headers= {"Authorization": f"Bearer {self.token}"},
                            params = params
                            ).json()
    

    def _post_request(self, endpoint, data=None):
        return requests.post(self.server_url + endpoint, 
                            json = data, 
                            headers= {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"})


    def get_burnin_data(self, filter=None):
        if not self.token:
            return
        db_data = []
        page = 1
        while True:
            response = requests.get(self.server_url + "/teste_burnin", 
                                    headers={'Content-Type': 'application/json',
                                            'Authorization': f'Bearer {self.token}', 
                                            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"},
                                    params={"per_page": 100,
                                            "page": page,
                                            "filter": filter
                                            }).json()
            if not response:
                break
            db_data.extend(response)
            page += 1
        df = pd.json_normalize(db_data)
        if df.empty:
            return df
        df['horario'] = pd.to_datetime(df['horario'], format='ISO8601')
        df = df.drop_duplicates(subset=['controladora_id'], keep="last")\
            .reset_index()
        df = df[~df['operador_id.nome'].isin(['Charles', 'Valciscley'])]
        return df
    
    def get_communication_data(self, filter):
        db_data = []
        page = 1
        while True:
            response = requests.get(self.server_url + "/teste_firmware", 
                                    headers={'Content-Type': 'application/json',
                                            'Authorization': f'Bearer {self.token}', 
                                            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"},
                                    params={"per_page": 100,
                                            "page": page,
                                            "filter": filter
                                            }).json()
            if not response:
                break
            db_data.extend(response)
            page += 1
        df = pd.json_normalize(db_data)
        df['horario'] = pd.to_datetime(df['horario'], format='ISO8601')
        df = df.drop_duplicates(subset=['controladora_id'], keep="last")\
            .reset_index()
        df = df[~df['operador_id.nome'].isin(['Charles', 'Valciscley'])]
        return df
    
    def get_power_data(self, filter):
        db_data = []
        page = 1
        while True:
            response = requests.get(self.server_url + "/teste_potencia", 
                                    headers={'Content-Type': 'application/json',
                                            'Authorization': f'Bearer {self.token}', 
                                            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"},
                                    params={"per_page": 100,
                                            "page": page,
                                            "filter": filter
                                            }).json()
            if not response:
                break
            db_data.extend(response)
            page += 1
        df = pd.json_normalize(db_data)
        df['horario'] = pd.to_datetime(df['horario'], format='ISO8601')
        df = df.drop_duplicates(subset=['controladora_id'], keep="last")\
            .reset_index()
        df = df[~df['operador_id.nome'].isin(['Charles', 'Valciscley'])]
        return df
    

    
    def get_status_data(self):
        db_data = []
        page = 1
        while True:
            response = requests.get(self.server_url + "/tcu", 
                                    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {self.token}'},
                                    params={"per_page": 100, "page": page}).json()
            if not response:
                break
            db_data.extend(response)
            page += 1
        df = pd.json_normalize(db_data)
        df = df.dropna(subset=['status.status_id.nome'])
        return df
    
    def get_tcu_history(self, serial_number):
        response = requests.get(self.server_url + f"/tcu/{serial_number}", 
                                headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {self.token}'},
                                ).json().get("status")
        df = pd.json_normalize(response)
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        df = df.sort_values('updated_at')
        df = df[["status_id.nome", "operador_id.nome", "created_at"]]
        
        return df

    def get_operators(self):
        operadores = [{"nome": user["nome"].rstrip(), "id": user["id"]} 
                      for user in requests.get(self.server_url + "/operador", headers={'Authorization': f'Bearer {self.token}'}).json()]
        return operadores
    
    def get_locals(self):
        locals = [{"nome": local["nome"].rstrip(), "id": local["id"]} 
                      for local in requests.get(self.server_url + "/status", headers={'Authorization': f'Bearer {self.token}'}).json()]
        return locals
    

    def change_tcu_status(self, serial_number, operator_id, status_id):
        data = {
            "controladora_id": serial_number,
            "status_id": status_id,
            "operador_id": operator_id
        }
        response = requests.post(self.server_url + "/status_tcu", json=data,  headers={'Authorization': f'Bearer {self.token}'})
        if response.status_code == 201:
            return {"success": True, "message": "Status alterado com sucesso!"}
        else:
            # Tentar retornar uma mensagem mais detalhada do servidor (se disponível)
            error_message = response.json().get("message", "Erro desconhecido")
            return {"success": False, "message": f"Falha ao alterar status: {error_message}"}
        

    def post_operator(self, nome, username):
        data = {
            "nome": nome,
            "empresa_id": 1,
            "username": username,
            "password": "12345678"
        }
        return self._post_request("operador", data)
    
    
    def get_etapa(self):
        return self._get_request("etapa")
        
    def post_etapa(self, nome):
        data = {
            "nome": nome
        }
        return self._post_request("etapa", data)
    
    def get_erro(self):
        erros = [{"nome": erro["nome"].rstrip(), "etapa": erro["etapa"]["nome"],  "id": erro["id"]} 
                      for erro in requests.get(self.server_url + "/erro", headers={'Authorization': f'Bearer {self.token}'}).json()]
        return erros
    

    def post_erro(self, etapa_id, nome):
        data = {
            "etapa_id": etapa_id,
            "nome": nome
        }
        return self._post_request("erro", data)
    

    def get_rft(self):
        return self._get_request("rft")
    
    def post_rft(self, controladora_id, operador_id, error_id, horario):
        data = {
            "controladora_id": controladora_id,
            "operador_id": operador_id,
            "erro_id": error_id,
            "horario": horario
        }
        return self._post_request("rft", data)


    def get_materials(self):
        return self._get_request("material")
    
    def post_material(self, codigo, descricao):
        data = {
            "id": codigo,
            "nome": descricao
        }
        return self._post_request("material", data)
    
    def get_solucao(self):
        return self._get_request("solucao")
    
    def post_solucao(self, nome):
        data = {
            "nome": nome
        }
        return self._post_request("solucao", data)
    

    def get_manutencao(self):
        return self._get_request("manutencao")

    def post_manutencao(self, operador_id, rft_id, solucao_id, horario, duracao):
        data = {
            "operador_id": operador_id,
            "rft_id": rft_id,
            "solucao_id": solucao_id,
            "horario": horario,
            "duracao": duracao
        }
        return self._post_request("manutencao", data)

    def get_perdas(self):
        return self._get_request("perdas")
    
    def post_perdas(self, material_id, manutencao_id, quantidade):
        data = {
            "material_id": material_id,
            "manutencao_id": manutencao_id,
            "quantidade": quantidade
        }
        return self._post_request("perdas", data)

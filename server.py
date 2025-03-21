import requests
import pandas as pd


class Server:
    def __init__(self):
        self.ip_addr = "https://ppc.tecsci.com.br/api/v1.0"
        self.token = None
        self.response = None
        self.excecao = None
        self.login()



    def login(self):
        try:
            response = requests.post(self.ip_addr + "/auth/login",
                                    headers={'Content-Type': 'application/json'}, 
                                    json={'username': 'gustavo.elias', 'password': '12345678'}).json()
            # self.token = response.get("access_token")
        except Exception as e:
            self.excecao = e.args
            # self.response = response

    def get_burnin_data(self, data):
        if not self.token:
            return
        db_data = []
        page = 1
        last_datetime = data
        while True:
            response = requests.get(self.ip_addr + "/teste_burnin", 
                                    headers={'Content-Type': 'application/json',
                                            'Authorization': f'Bearer {self.token}', 
                                            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"},
                                    params={"per_page": 100,
                                            "page": page,
                                            "filter": f"datetime >= '{last_datetime}'"
                                            }).json()
            if not response:
                break
            db_data.extend(response)
            page += 1
        df = pd.json_normalize(db_data)
        df['horario'] = pd.to_datetime(df['horario'], format='ISO8601')
        df = df.drop_duplicates(subset=['controladora_id'], keep="last")\
            .reset_index()
        return df
    
    def get_communication_data(self, data):
        db_data = []
        page = 1
        last_datetime = data
        while True:
            response = requests.get(self.ip_addr + "/teste_firmware", 
                                    headers={'Content-Type': 'application/json',
                                            'Authorization': f'Bearer {self.token}', 
                                            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"},
                                    params={"per_page": 100,
                                            "page": page,
                                            "filter": f"datetime >= '{last_datetime}'"
                                            }).json()
            if not response:
                break
            db_data.extend(response)
            page += 1
        df = pd.json_normalize(db_data)
        df['horario'] = pd.to_datetime(df['horario'], format='ISO8601')
        df = df.drop_duplicates(subset=['controladora_id'], keep="last")\
            .reset_index()
        return df
    
    def get_power_data(self, data):
        db_data = []
        page = 1
        last_datetime = data
        while True:
            response = requests.get(self.ip_addr + "/teste_potencia", 
                                    headers={'Content-Type': 'application/json',
                                            'Authorization': f'Bearer {self.token}', 
                                            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"},
                                    params={"per_page": 100,
                                            "page": page,
                                            "filter": f"datetime >= '{last_datetime}'"
                                            }).json()
            if not response:
                break
            db_data.extend(response)
            page += 1
        df = pd.json_normalize(db_data)
        df['horario'] = pd.to_datetime(df['horario'], format='ISO8601')
        df = df.drop_duplicates(subset=['controladora_id'], keep="last")\
            .reset_index()
        return df

    
    def get_status_data(self):
        db_data = []
        page = 1
        while True:
            response = requests.get(self.ip_addr + "/tcu", 
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
        response = requests.get(self.ip_addr + f"/tcu/{serial_number}", 
                                headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {self.token}'},
                                ).json().get("status")
        df = pd.json_normalize(response)
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        df = df.sort_values('updated_at')
        df = df[["status_id.nome", "operador_id.nome", "created_at"]]
        
        return df

    def get_operators(self):
        operadores = [{"nome": user["nome"].rstrip(), "id": user["id"]} 
                      for user in requests.get(self.ip_addr + "/operador", headers={'Authorization': f'Bearer {self.token}'}).json()]
        return operadores
    
    def get_locals(self):
        locals = [{"nome": local["nome"].rstrip(), "id": local["id"]} 
                      for local in requests.get(self.ip_addr + "/status", headers={'Authorization': f'Bearer {self.token}'}).json()]
        return locals
    

    def change_tcu_status(self, serial_number, operator_id, status_id):
        data = {
            "controladora_id": serial_number,
            "status_id": status_id,
            "operador_id": operator_id
        }
        response = requests.post(self.ip_addr + "/status_tcu", json=data,  headers={'Authorization': f'Bearer {self.token}'})
        if response.status_code == 201:
            return {"success": True, "message": "Status alterado com sucesso!"}
        else:
            # Tentar retornar uma mensagem mais detalhada do servidor (se disponível)
            error_message = response.json().get("message", "Erro desconhecido")
            return {"success": False, "message": f"Falha ao alterar status: {error_message}"}




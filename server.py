import requests
import pandas as pd


class Server:
    def __init__(self):
        self.ip_addr = "https://ppc.tecsci.com.br/api/v1.0"
        self.token = None
        self.df = None
        self.login()
        self.get_burnin_data()


    def login(self):
        response = requests.post(self.ip_addr + "/auth/login",
                   headers={'Content-Type': 'application/json'}, 
                   json={'username': 'gustavo.elias', 'password': '12345678'}).json()
        self.token = response.get("access_token")

    def get_burnin_data(self):
        db_data = []
        page = 1
        while True:
            response = requests.get(self.ip_addr + "/teste_burnin", 
                                    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {self.token}'},
                                    params={"per_page": 100, "page": page}).json()
            if not response:
                break
            db_data.extend(response)
            page += 1
        df = pd.json_normalize(db_data)
        df['horario'] = pd.to_datetime(df['horario'])
        data_limite = pd.Timestamp('2024-09-15', tz='UTC')
        df = df[df['horario'] >= data_limite]
        df = df.drop_duplicates(subset=['controladora_id'], keep="last")
        df = df.reset_index()
        # df = df[df['controladora_id'].str.startswith('0124')]
        self.df = df




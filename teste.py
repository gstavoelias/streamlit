from utils import Server, User


api = Server()
api.login(User("gustavo.elias", "12345678"))
data = {
        'rft_id': 266, 
        'descricao': 'Reinvertido chicote de entrada DC/BAT', 
        'solucao_id': 5, 
        'operador_id': 18, 
        'horario': '2025-05-27T15:01:45:18900', 
        'duracao': 20
        }
response = api.post_manutencao(operador_id=18, rft_id=266, solucao_id=5, descricao='Reinvertido chicote de entrada DC/BAT', horario='2025-05-27',
                    duracao=20)
print(response.status_code)
if response != 201:
    print(response.json)
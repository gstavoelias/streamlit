import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from server import Server
from datetime import datetime, timedelta

# Inicializa a API Flask para buscar os dados
server = Server()

# Inicializa o app Dash com tema escuro
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Banco de Dados TECSCI"

# Função para definir o início do período selecionado
def get_start_date(period):
    hoje = datetime.today()
    if period == "SEMANA":
        return hoje - timedelta(days=hoje.weekday())  # Segunda-feira
    elif period == "MÊS":
        return hoje.replace(day=1)  # Primeiro dia do mês
    elif period == "SEMESTRE":
        primeiro_mes_do_semestre = 1 if hoje.month <= 6 else 7  # Janeiro ou Julho
        return hoje.replace(month=primeiro_mes_do_semestre, day=1)
    elif period == "ANO":
        return hoje.replace(month=1, day=1)  # Primeiro dia do ano
    return None  # TOTAL → Sem limite inferior

# Layout do Dashboard
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(html.H1("Dashboard - Burn In", className="text-center text-light"), width=12)
        ),
        dbc.Row(
            dbc.Col(dcc.Dropdown(
                id="period-selector",
                options=[
                    {"label": "Semana", "value": "SEMANA"},
                    {"label": "Mês", "value": "MÊS"},
                    {"label": "Semestre", "value": "SEMESTRE"},
                    {"label": "Ano", "value": "ANO"},
                    {"label": "Total", "value": "TOTAL"},
                ],
                value="SEMANA",
                clearable=False,
                style={"color": "black"}  # Mantém a cor do texto legível
            ), width=4),
            className="mb-3"
        ),
        dbc.Row(
            dbc.Col(dcc.Graph(id="bar-chart"), width=12)
        ),
        dbc.Row(
            dbc.Col([
                html.H3("Duração dos testes:", className="text-light"),
                html.P(id="duration-mean", className="text-light"),
                html.P(id="duration-max", className="text-light"),
                html.P(id="duration-min", className="text-light"),
            ])
        ),
        dbc.Row(
            dbc.Col(
                dbc.Button("Mostrar Base de Dados", id="toggle-table", color="primary", className="mb-2"),
                width=12
            )
        ),
        dbc.Collapse(
            dbc.Row(dbc.Col(dcc.Loading(dash_table.DataTable(id="data-table", style_table={"overflowX": "auto"})))),
            id="table-collapse",
            is_open=False,
        )
    ],
    fluid=True,
)

# Callback para atualizar os dados e gráficos
@app.callback(
    [
        Output("bar-chart", "figure"),
        Output("duration-mean", "children"),
        Output("duration-max", "children"),
        Output("duration-min", "children"),
        Output("data-table", "data"),
        Output("data-table", "columns"),
    ],
    [Input("period-selector", "value")]
)
def update_dashboard(selected_period):
    start_date = get_start_date(selected_period)
    df = server.get_burnin_data(start_date)

    # Gráfico de barras
    data = df.groupby(df["horario"].dt.date).size().reset_index(name="count")
    fig = px.bar(data, x="horario", y="count", title="Testes por dia", template="plotly_dark")

    # Estatísticas de duração
    mean_duration = f"Média: {df['duracao'].mean():.2f}"
    max_duration = f"Máximo: {df['duracao'].max():.2f}"
    min_duration = f"Mínimo: {df['duracao'].min():.2f}"

    # Tabela de dados
    columns = [{"name": col, "id": col} for col in df.columns]
    return fig, mean_duration, max_duration, min_duration, df.to_dict("records"), columns

# Callback para exibir/esconder a tabela
@app.callback(
    Output("table-collapse", "is_open"),
    [Input("toggle-table", "n_clicks")],
    prevent_initial_call=True
)
def toggle_table(n_clicks):
    return True

# Executa o app
if __name__ == "__main__":
    app.run(debug=True)

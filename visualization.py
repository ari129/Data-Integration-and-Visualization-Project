import pandas as pd
import plotly.express as px
from dash import dcc, html, dash_table, Dash
from dash.dependencies import Input, Output

# Leer el archivo winners_clean.csv
winners = pd.read_csv('winners_clean.csv')

# Contar cuántos mundiales ha ganado cada país
world_cup_wins = winners \
    .groupby("Winner", as_index=False) \
    .size() \
    .rename(columns={"Winner": "Country", "size": "Total_Wins"}) \
    .sort_values("Total_Wins", ascending=False)

# Preparar la tabla: Resumen de mundiales
summary_table = winners.groupby("Winner", as_index=False).agg(
    Matches_Played=('MatchesPlayed', 'sum'),
    Goals_Scored=('GoalsScored', 'sum'),
    World_Cups_Won=('Year', 'count'),
    Attendance=('Attendance', 'sum')
).rename(columns={"Winner": "Country"}).sort_values("World_Cups_Won", ascending=False)

# Calcular cuántos mundiales ganó cada país en casa
home_wins = winners[winners['Country'] == winners['Winner']].groupby('Winner').size()
summary_table["World_Cups_Won_at_Home"] = summary_table["Country"].map(home_wins).fillna(0).astype(int)

# Crear la aplicación Dash
app = Dash(__name__)

# Layout de la aplicación
app.layout = html.Div([
    html.H1("ANALYSIS OF THE WORLD CUP", style={'text-align': 'center'}),

    # Sección del dropdown y el mapa
    html.Div([
        html.H3("Map: World Cups Won per Country", style={'text-align': 'center'}),
        dcc.Dropdown(
            id='country_dropdown',
            options=[{'label': country, 'value': country} for country in world_cup_wins['Country']],
            placeholder="Choose a country",
            multi=False
        ),
        dcc.Graph(id='choropleth_map', style={'height': '80vh'})
    ], style={'margin-bottom': '50px'}),

    # Sección de la tabla
    html.Div([
        html.H3("Table: Summary of World Cups Won", style={'text-align': 'center'}),
        dash_table.DataTable(
            id='winners_table',
            columns=[
                {"name": "Country", "id": "Country"},
                {"name": "World Cups Won", "id": "World_Cups_Won"},
                {"name": "World Cups Won at Home", "id": "World_Cups_Won_at_Home"},
            ],
            data=summary_table.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center'},
            style_header={'backgroundColor': 'lightblue', 'fontWeight': 'bold'},
            page_size=10  # Mostrar 10 filas por página
        )
    ])
])

# Callback para actualizar el gráfico según el país seleccionado
@app.callback(
    Output('choropleth_map', 'figure'),
    [Input('country_dropdown', 'value')]
)
def update_map(selected_country):
    # Filtrar los datos según el país seleccionado
    if selected_country:
        filtered_data = world_cup_wins[world_cup_wins['Country'] == selected_country]
    else:
        filtered_data = world_cup_wins

    # Crear el gráfico de coropletas
    fig = px.choropleth(filtered_data,
                        locations="Country",
                        locationmode="country names",
                        color="Total_Wins",
                        hover_name="Country",
                        title="World Cups Won per Country",
                        color_continuous_scale=px.colors.sequential.Plasma)
    return fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)

"""# Leer el archivo goalscorers_cleaned.csv
goalscorers = pd.read_csv('goalscorers_cleaned.csv')

# Agrupar los goles por equipo
total_goals_by_country = goalscorers \
    .groupby("team", as_index=False) \
    .sum("goals") \
    .rename(columns={"goals": "total_goals"}) \
    .sort_values("total_goals", ascending=False)

# Crear el gráfico de coropletas
fig = px.choropleth(total_goals_by_country, 
                    locations="team",
                    locationmode="country names",
                    color="total_goals",
                    hover_name="team",
                    title="Total de goles por país")
fig.show()"""
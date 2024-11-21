import pandas as pd
import plotly.express as px
from dash import dcc, html, dash_table, Dash
from dash.dependencies import Input, Output

# Read the files
winners = pd.read_csv('winners_clean.csv')
goalscorers = pd.read_csv('goalscorers_cleaned.csv')
scorer_worldcup = pd.read_csv('scorer_worldcup.csv')

# Contar cuántos mundiales ha ganado cada país
world_cup_wins = winners['Winner'].value_counts().reset_index()
world_cup_wins.columns = ['Country', 'Total_Wins']

# Crear una tabla resumen
summary_table = winners.groupby("Winner", as_index=False).agg(
    World_Cups_Won=('Year', 'count')
).rename(columns={"Winner": "Country"}).sort_values("World_Cups_Won", ascending=False)

# Calcular cuántos mundiales ganó cada país en casa
home_wins = winners[winners['Country'] == winners['Winner']].groupby('Winner').size()
summary_table["World_Cups_Won_at_Home"] = summary_table["Country"].map(home_wins).fillna(0).astype(int)

# Calcular total de goles por país
total_goals_by_country = goalscorers \
    .groupby("team", as_index=False) \
    .sum("goals") \
    .rename(columns={"goals": "total_goals"}) \
    .sort_values("total_goals", ascending=False)
    
# Winner for each World Cup
winners_per_year = winners[['Year', 'Winner']]

# Obtener el máximo goleador de cada Mundial
top_scorers = scorer_worldcup.groupby("Year").apply(lambda x: x.loc[x['Goals'].idxmax()]).reset_index(drop=True)
top_scorers = top_scorers[['Year', 'Name', 'Goals']].rename(columns={'Name': 'Top_Scorer', 'Goals': 'Goals_Scored'})

# Crear un DataFrame con Año, Ganador y Máximo Goleador
world_cup_summary = pd.merge(winners_per_year, top_scorers, on="Year")
world_cup_summary = world_cup_summary[['Year', 'Winner', 'Top_Scorer', 'Goals_Scored']]

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
            options=[{'label': team, 'value': team} for team in total_goals_by_country['team']],
            placeholder="Choose a country",
            multi=False
        ),
        dcc.Graph(id='choropleth_map', style={'height': '80vh'})
    ], style={'margin-bottom': '50px'}),

    # Sección de la tabla
    html.Div([
        # Contenedor para tabla y texto
        html.Div([
            # Tabla
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
            ], style={'width': '60%', 'display': 'inline-block', 'vertical-align': 'top'}),

            # Texto a la derecha de la tabla
            html.Div([
                html.P(
                    "As we can see in the table, throughout history, whether the winning team played at home or not does not seem to have a great influence.",
                    style={'fontSize': '16px', 'lineHeight': '1.6'}
                )
            ], style={'width': '35%', 'display': 'inline-block', 'padding-left': '20px', 'vertical-align': 'top'})
        ], style={'display': 'flex'})
    ]),
    
    html.Div([
        html.H3("World Cup Summary: Winner and Top Scorer", style={'text-align': 'center'}),
        dash_table.DataTable(
            id='world_cup_summary_table',
            columns=[
                {"name": "Year", "id": "Year"},
                {"name": "Winner", "id": "Winner"},
                {"name": "Top Scorer", "id": "Top_Scorer"},
                {"name": "Goals Scored", "id": "Goals_Scored"},
            ],
            data=world_cup_summary.to_dict('records'),
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
        filtered_data = total_goals_by_country[total_goals_by_country['team'] == selected_country]
    else:
        filtered_data = total_goals_by_country

    # Crear el gráfico de coropletas
    fig = px.choropleth(
        filtered_data,
        locations="team",
        locationmode="country names",
        color="total_goals",
        hover_name="team",
        title="Goals of the maximun scorer of each country",
        color_continuous_scale=px.colors.sequential.Plasma
    )
    return fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)


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
                    title="Goals of the maximun scorer of each country")
fig.show()

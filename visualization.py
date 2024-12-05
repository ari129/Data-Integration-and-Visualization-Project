import pandas as pd
import plotly.express as px
from dash import dcc, html, dash_table, Dash
from dash.dependencies import Input, Output

# Read the files
winners = pd.read_csv('winners_clean.csv')
goalscorers = pd.read_csv('goalscorers_cleaned.csv')
scorer_worldcup = pd.read_csv('scorer_worldcup.csv')
summary_results = pd.read_csv('summary_combined.csv')


# Create the summary table for the first chart
summary_table = winners.groupby("Winner", as_index=False).agg(
    World_Cups_Won=('Year', 'count')
).rename(columns={"Winner": "Country"}).sort_values("World_Cups_Won", ascending=False)
# Calculate how many world cups were won at home
home_wins = winners[winners['Country'] == winners['Winner']].groupby('Winner').size()
summary_table["World_Cups_Won_at_Home"] = summary_table["Country"].map(home_wins).fillna(0).astype(int)
# Winner and Top Scorer for each World Cup (for second chart)
winners_per_year = winners[['Year', 'Winner']]
top_scorers = scorer_worldcup.groupby("Year").apply(lambda x: x.loc[x['Goals'].idxmax()]).reset_index(drop=True)
top_scorers = top_scorers[['Year', 'Name', 'Goals']].rename(columns={'Name': 'Top_Scorer', 'Goals': 'Goals_Scored'})
world_cup_summary = pd.merge(winners_per_year, top_scorers, on="Year")

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
    html.Div([
        html.Img(
            src=app.get_asset_url('image1.png'),
            style={
                'width': '50%',  
                'height': 'auto',  
                'display': 'block',
                'margin': '0 auto'
            }
        )
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),
    html.H1("ANALYSIS OF THE WORLD CUP", style={'text-align': 'center'}),

    # Sección del dropdown y el mapa
    html.Div([
        html.H3("Select Metric for the Map:", style={'text-align': 'center'}),
        dcc.Dropdown(
            id='metric_dropdown',
            options=[
                {'label': 'Wins', 'value': 'Wins'},
                {'label': 'Losses', 'value': 'Losses'},
                {'label': 'Home Wins', 'value': 'Home Wins'}
            ],
            value='Wins',  # Métrica por defecto
            style={'width': '50%', 'margin': '0 auto'}
        )
    ], style={'margin-bottom': '30px'}),
    
   html.Div([
        dcc.Graph(id='choropleth_map', style={'height': '80vh'})
    ]), 

        # Bar chart for world cups won
    html.Div([
        html.H3("Bar Chart: World Cups Won and Won at Home", style={'text-align': 'center'}),
        dcc.Graph(id='bar_chart')
    ]),
    
        # Visualization for second table
    html.Div([
        html.H3("Visualization: Top Scorers and World Cup Winners", style={'text-align': 'center'}),
        dcc.Graph(id='line_chart')
    ]),

])


# Callback para actualizar el gráfico según el país seleccionado
@app.callback(
    Output('choropleth_map', 'figure'),
    [Input('metric_dropdown', 'value')]
)

def update_map(selected_metric):
    # Crear el gráfico de coropletas
    fig = px.choropleth(
        summary_results,
        locations="Country",
        locationmode="country names",
        color=selected_metric,
        hover_name="Country",
        title=f"World Cup Metric: {selected_metric}",
        color_continuous_scale=px.colors.sequential.Viridis
    )
    return fig

@app.callback(
    Output('bar_chart', 'figure'),
    [Input('bar_chart', 'id')]
)
def update_bar_chart(_):
    fig = px.bar(
        summary_table,
        x="Country",
        y=["World_Cups_Won", "World_Cups_Won_at_Home"],
        barmode="group",
        labels={"value": "World Cups", "variable": "Category"},
        title="World Cups Won and Won at Home",
        text_auto=True
    )
    fig.update_layout(
        legend=dict(title="Category", orientation="h", x=0.5, xanchor="center", y=1.1),
        xaxis_title="Country",
        yaxis_title="Number of World Cups",
    )
    return fig


@app.callback(
    Output('line_chart', 'figure'),
    [Input('line_chart', 'id')]
)
def update_line_chart(_):
    fig = px.scatter(
        world_cup_summary,
        x="Year",
        y="Goals_Scored",
        color="Winner",
        hover_data={"Top_Scorer": True},
        title="Top Scorers and Goals Scored by Year",
        labels={"Goals_Scored": "Goals Scored", "Year": "World Cup Year"},
        text="Top_Scorer"
    )
    fig.update_traces(marker=dict(size=12), textposition="top center")
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
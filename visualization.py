import pandas as pd
import plotly.express as px
import dash
import dash_html_components as html


""""
results = pd.read_csv('results.csv')

world_cup_res = results \
	.query('tournament == "FIFA World Cup"')

away_goals = world_cup_res \
    .filter(["away_team", "away_score"]) \
	.rename(columns = {"away_team": "team", "away_score": "score"}) 

home_goals = world_cup_res \
    .filter(["home_team", "home_score"]) \
	.rename(columns = {"home_team": "team", "home_score": "score"}) 

total_goals_by_country = pd.concat([home_goals, away_goals]) \
	.groupby("team", as_index=False) \
    .sum("score") \
	.rename(columns = {"score": "total_goals"}) \
	.sort_values("total_goals", ascending=False)

fig = px.choropleth(total_goals_by_country, 
                    locations="team",
                    locationmode="country names",
                    color="total_goals",
                    hover_name="team")
fig.show()"""""



# Leer el archivo goalscorers_cleaned.csv
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
fig.show()

import pandas as pd
# Read results.csv. Assign to results.
results = pd.read_csv('results.csv')
shootouts = pd.read_csv('shootouts.csv')
winners = pd.read_csv('winners.csv')

#we check if there is any duplicated match
if(results.duplicated().sum()!=0):
    print("The are duplicate matches in the files you have entered!")
    # We eliminate duplicate results
    results_clean = results.drop_duplicates(subset=['date', 'home_team', 'away_team', 'tournament'], keep='first')
    results_clean.to_csv('results_clean.csv', index=False)

if(shootouts.duplicated().sum()!=0):
    print("The are duplicate shootouts in the files you have entered!")
    # We eliminate duplicate results
    shootouts_clean = shootouts.drop_duplicates(subset=['date', 'home_team', 'away_team', 'winner'], keep='first')
    shootouts_clean.to_csv('shootouts_clean.csv', index=False)
    
if(winners.duplicated().sum()!=0):
    print("The are duplicate winners in the files you have entered!")
    # We eliminate duplicate results
    winners_clean = winners.drop_duplicates(subset=['Year', 'Country', 'Winner', 'Runners-Up'], keep='first')
    winners_clean.to_csv('winners_clean.csv', index=False)


victorias_por_pais = winners_clean.groupby(['Year', 'Winner']).size().reset_index(name='Victorias')

# Guardar el resultado en un nuevo archivo CSV
victorias_por_pais.to_csv('victorias_por_pais.csv', index=False)



# Unir results con shootouts basado en date, home_team, y away_team
#merged_data = pd.merge(results_clean, shootouts_clean, how='left', on=['date', 'home_team', 'away_team'])

# Extraer el año de la columna "date" para usarlo en la unión con winners.csv
#merged_data['year'] = pd.to_datetime(merged_data['date']).dt.year

# Unir los datos resultantes con los datos de ganadores y torneos
#merged_data = pd.merge(merged_data, winners_clean, how='left', left_on=['year', 'home_team'], right_on=['Year', 'Country'])

# Revisar las primeras filas del archivo combinado
#print(merged_data.head())

# Guardar el archivo final como CSV
#merged_data.to_csv('merged_football_data.csv', index=False)

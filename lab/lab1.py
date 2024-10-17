import sqlite3
import pandas as pd


##CLEAN SECTION

# Function to clean a DataFrame
def limpiar_dataframe(df):
    # Delete rows with null values
    df = df.dropna()
    return df

# Reeds results.csv
results = pd.read_csv('results.csv')
# Clean and delete duplicates in results
results_limpio = limpiar_dataframe(results)
if results.duplicated().sum() != 0:
    print("There are duplicate matches in results.csv!")
    results_limpio = results_limpio.drop_duplicates(subset=['date', 'home_team', 'away_team', 'tournament'], keep='first')

# Save the cleaned DataFrame to a file CSV
results_limpio.to_csv('results_clean.csv', index=False)

# Reeds shootouts.csv
shootouts = pd.read_csv('shootouts.csv')
# Clean and delete duplicates in shootouts
shootouts_limpio = limpiar_dataframe(shootouts)
if shootouts.duplicated().sum() != 0:
    print("There are duplicate shootouts in the shootouts file!")
    shootouts_limpio = shootouts_limpio.drop_duplicates(subset=['date', 'home_team', 'away_team', 'winner'], keep='first')

# Save the cleaned DataFrame to a file CSV
shootouts_limpio.to_csv('shootouts_clean.csv', index=False)

# Connect to in-memory database (or use 'winners.db' for persistence)
conexion = sqlite3.connect(':memory:')

# Reeds winners.sql and execute Sql statements
with open('winners.sql', 'r') as f:
    sql_script = f.read()

# Execute CREATE TABLE e INSERTS
conexion.executescript(sql_script)

# Reeds data of 'winners'
winners = pd.read_sql_query("SELECT * FROM winners", conexion)

# Clean and delete duplicates in winners
winners_limpio = limpiar_dataframe(winners)
if winners.duplicated().sum() != 0:
    print("There are duplicate winners in the winners table!")
    winners_limpio = winners_limpio.drop_duplicates(subset=['Year', 'Country', 'Winner', 'Runners-Up'], keep='first')

# Save the cleaned DataFrame to a file CSV
winners_limpio.to_csv('winners_clean.csv', index=False)

# Close the conexion
conexion.close()

print("CSV files have been successfully cleaned and saved.")


##READING AND SELECTING DATA SECTION 

#SHOOTOUTS

# Initialize a list to store the data
resumen = []

# Get all countries of home and visiting teams
equipos = pd.concat([shootouts['home_team'], shootouts['away_team']]).unique()

# Calculate the results for each country
for pais in equipos:
    # Counting games played
    partidos_jugados = (shootouts['home_team'] == pais).sum() + (shootouts['away_team'] == pais).sum()
    
    # Counting victories
    victorias = (shootouts['winner'] == pais).sum()

    # Counting defeats (games played - wins)
    derrotas_count = partidos_jugados - victorias

    # Add the results to the list
    resumen.append({
        'Country': pais,
        'Matches Played': partidos_jugados,
        'Wins': victorias,
        'Losses': derrotas_count
    })

# Create a DataFrame from list
resumen_paises = pd.DataFrame(resumen)

# Save the summary in a CSV file
resumen_paises.to_csv('summary_shootouts.csv', index=False)

print("File 'summary_shootouts.csv' was created.")

#RESULTS
"""
# Initialize a list to store the data
resumen2 = []

# Get all countries of home and visiting teams
equipos2 = pd.concat([results['home_team'], results['away_team']]).unique()

# Calculate the results for each country
for pais in equipos2:
    # Counting games played
    partidos_jugados = (results['home_team'] == pais).sum() + (results['away_team'] == pais).sum()
    
    # Counting victories
    victorias = 0
    victorias_en_casa = 0
    
    # Calculate overall and home wins
    for index, row in results.iterrows():
        if row['home_team'] == pais and row['home_score'] > row['away_score']:
            victorias += 1
            victorias_en_casa += 1
        elif row['away_team'] == pais and row['away_score'] > row['home_score']:
            victorias += 1
    
    # Counting defeats
    derrotas_count = partidos_jugados - victorias

    # Add the results to the list
    resumen2.append({
        'Country': pais,
        'Matches Played': partidos_jugados,
        'Wins': victorias,
        'Losses': derrotas_count,
        'Home Wins': victorias_en_casa
    })

# Create a DataFrame from list
resumen2_paises = pd.DataFrame(resumen2)

# Save the summary in a CSV file
resumen2_paises.to_csv('summary_results.csv', index=False)

print("File 'summary_results.csv' was created.")
"""

#RESULTS + WINNERS

resumen_paises = pd.read_csv('summary_results.csv')

# Initialize columns for world championships won and locations
resumen_paises['World Cups Won'] = 0
resumen_paises['World Cup Locations'] = ''

# Counting World Cup wins and placements
for index, row in resumen_paises.iterrows():
    pais = row['Country']
    # Counting world championships won
    mundiales_ganados = winners[winners['Winner'] == pais].shape[0]
    
    # Obtain the places of the world championships won
    lugares_mundiales = winners[winners['Winner'] == pais]['Country'].tolist()
    
    # Assign values to the DataFrame
    resumen_paises.at[index, 'World Cups Won'] = mundiales_ganados
    resumen_paises.at[index, 'World Cup Locations'] = ', '.join(lugares_mundiales)  # Convertir la lista a una cadena

# Save the updated summary in a new CSV file
resumen_paises.to_csv('summary_by_country_full.csv', index=False)

print("File 'summary_by_country_full.csv' was created.")

##MERGE OF ALL THE FILES

#SUMMARY_BY_COUNTRY_FULL + SUMMARY_RESULTS

resumen_paises = pd.read_csv('summary_by_country_full.csv')
resumen_shootouts = pd.read_csv('summary_shootouts.csv')

# Rename the column of victories in shootouts to avoid conflicts.
resumen_shootouts.rename(columns={'Wins': 'Shootout Wins'}, inplace=True)

# Join the two DataFrames by the column 'Country'.
resumen_completo = pd.merge(resumen_paises, resumen_shootouts[['Country', 'Shootout Wins']], on='Country', how='left')

# Saving the combined summary in a new CSV file
resumen_completo.to_csv('summary_combined.csv', index=False)

print("The combined summary has been saved in 'summary_combined.csv'.")
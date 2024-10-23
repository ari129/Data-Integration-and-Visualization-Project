import sqlite3
import pandas as pd

## CLEAN SECTION

# Function to clean a DataFrame
def limpiar_dataframe(df):
    # Delete rows with null values
    df = df.dropna()
    return df

# Reads results.csv
results = pd.read_csv('results.csv')
# Clean and delete duplicates in results
results_limpio = limpiar_dataframe(results)
if results.duplicated().sum() != 0:
    print("There are duplicate matches in results.csv!")
    results_limpio = results_limpio.drop_duplicates(subset=['date', 'home_team', 'away_team', 'tournament'], keep='first')

# Save the cleaned DataFrame to a file CSV
results_limpio.to_csv('results_clean.csv', index=False)

# Reads shootouts.csv
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

# Reads winners.sql and execute SQL statements
with open('winners.sql', 'r') as f:
    sql_script = f.read()

# Execute CREATE TABLE and INSERTS
conexion.executescript(sql_script)

# Reads data of 'winners'
winners = pd.read_sql_query("SELECT * FROM winners", conexion)

# Clean and delete duplicates in winners
winners_limpio = limpiar_dataframe(winners)
if winners.duplicated().sum() != 0:
    print("There are duplicate winners in the winners table!")
    winners_limpio = winners_limpio.drop_duplicates(subset=['Year', 'Country', 'Winner', 'Runners-Up'], keep='first')

# Save the cleaned DataFrame to a file CSV
winners_limpio.to_csv('winners_clean.csv', index=False)

# Close the connection
conexion.close()

print("CSV files have been successfully cleaned and saved.")


## READING AND SELECTING DATA SECTION 

# SHOOTOUTS

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

# RESULTS + WINNERS

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
    resumen_paises.at[index, 'World Cup Locations'] = ', '.join(lugares_mundiales)  # Convert the list to a string

# Save the updated summary in a new CSV file
resumen_paises.to_csv('summary_by_country_full.csv', index=False)

print("File 'summary_by_country_full.csv' was created.")


## GOALSCORERS SECTION (included directly into the merge)

# Load the goalscorers file
goalscorers_df = pd.read_csv('goalscorers.csv')

# Clean the data by removing own goals and dropping unnecessary columns
cleaned_goals_df = goalscorers_df[goalscorers_df['own_goal'] == False].drop(columns=['date', 'home_team', 'away_team', 'minute', 'own_goal', 'penalty'])

# Group by team and scorer to count the number of goals for each scorer in each country (team)
scorer_count_df = cleaned_goals_df.groupby(['team', 'scorer']).size().reset_index(name='goals')

# Sort the scorers within each country by the number of goals in descending order
ranked_scorers_df = scorer_count_df.sort_values(['team', 'goals'], ascending=[True, False])

# Get the best goalscorer for each country by selecting the first entry after grouping by team
best_scorers_df = ranked_scorers_df.groupby('team').first().reset_index()


## MERGE OF ALL THE FILES INCLUDING GOALSCORERS

# SUMMARY_BY_COUNTRY_FULL + SUMMARY_RESULTS + GOALSCORERS

resumen_paises = pd.read_csv('summary_by_country_full.csv')
resumen_shootouts = pd.read_csv('summary_shootouts.csv')

# Rename the column of victories in shootouts to avoid conflicts.
resumen_shootouts.rename(columns={'Wins': 'Shootout Wins'}, inplace=True)

# Join the two DataFrames by the column 'Country'.
summary_combined = pd.merge(resumen_paises, resumen_shootouts[['Country', 'Shootout Wins']], on='Country', how='left')

# Merge the best goalscorers data into the combined summary by matching the 'Country' column with the 'team' column from the goalscorers data
# Note: The goalscorers data is added, but the DataFrame name remains 'summary_combined'
summary_combined = pd.merge(summary_combined, best_scorers_df[['team', 'scorer', 'goals']], left_on='Country', right_on='team', how='left')

# Drop the redundant 'team' column from the merged result
summary_combined = summary_combined.drop(columns=['team'])

# Saving the final combined summary into a new CSV file
summary_combined.to_csv('summary_combined.csv', index=False)

print("The final summary, including goalscorers, has been saved in 'summary_combined.csv'.")

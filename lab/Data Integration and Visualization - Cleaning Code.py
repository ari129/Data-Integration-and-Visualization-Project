import pandas as pd
# Read results.csv. Assign to results.
results = pd.read_csv('results.csv')
shootouts = pd.read_csv('shootouts.csv')
goalscorers = pd.read_csv('winners.csv')

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
    
if(goalscorers.duplicated().sum()!=0):
    print("The are duplicate winners in the files you have entered!")
    # We eliminate duplicate results
    goalscorers_clean = goalscorers.drop_duplicates(subset=['Year', 'Country', 'Winner', 'Runners-Up'], keep='first')
    goalscorers_clean.to_csv('goalscorers_clean.csv', index=False)


#combined_results = pd.merge(results, shootouts, on=['date', 'home_team', 'away_team'], how='left')
#combined_with_goals = pd.merge(combined_results, goalscorers, on=['date', 'home_team', 'away_team'], how='left')
# Guardar en un CSV
#combined_with_goals.to_csv('integrated_results.csv', index=False)
import os
import pandas as pd
import numpy as np
from unidecode import unidecode
from datetime import datetime
import itertools

file_names = os.listdir("data")


# To be applied immediately after parsing, before storing anywhere:
def clean_team_names(file_name):
    # file_name = file_names[0]
    bookmaker, country, league = file_name.lower().replace(".", "").replace("csv", "").split("-")
    df = pd.read_csv("data/" + file_name)
    df["bookmaker"] = bookmaker
    df["country"] = country
    df["league"] = league

    # Akzente ersetzen mit unidecode:
    df["home"] = df["home"].apply(unidecode)
    df["guest"] = df["guest"].apply(unidecode)

    df["date"] = df["date"].apply(lambda value: datetime.strptime(value, "%d.%m.%Y"))

    df.to_csv("data_new/" + file_name, index=False)
    return df

dfs_new = [clean_team_names(file_name) for file_name in file_names]

df_teams = pd.concat(dfs_new, axis=0)

df_teams = df_teams[["country", "league", "home", "guest"]] \
    .melt(id_vars=['country', 'league'], value_vars=['home', 'guest'], value_name="team") \
    .drop(columns="variable") \
    .drop_duplicates()

df_teams.to_excel("teams.xlsx", index=False)

# Tabelle returnen, ausserhalb zusammenfuegen
# nach Excel exportieren und Ergebnis checken



#### 

dfs = [pd.read_csv("data_new/" + file_name) for file_name in file_names]
len(dfs)

df = pd.concat(dfs, axis=0)

df_teams = pd.read_excel("teams.xlsx")
df = df.join(df_teams.set_index(['country', 'league', 'team'], drop=True).rename(columns={'id': 'id_home'}), on=['country', 'league', 'home'])
df = df.join(df_teams.set_index(['country', 'league', 'team'], drop=True).rename(columns={'id': 'id_guest'}), on=['country', 'league', 'guest'])


df[['1', 'X', '2', '1X', '12', 'X2', 'goals_threshold', '+', '-', 'J', 'N']] = df[['1', 'X', '2', '1X', '12', 'X2', 'goals_threshold', '+', '-', 'J', 'N']] \
    .apply(lambda col: col.astype('string')) \
    .apply(lambda col: col.str.replace(",", ".").astype('float'))


# df.to_excel("combined.xlsx")

# df[['1', 'X', '2', '1X', '12', 'X2', 'goals_threshold', '+', '-', 'J', 'N']] = df[['1', 'X', '2', '1X', '12', 'X2', 'goals_threshold', '+', '-', 'J', 'N']] \
#     .fillna(value=1)




#### Eigentliche Berechnung / Arbitrage-Abfrage würde hier beginnen ####

df = df.pivot(
    index=['date', 'id_home', 'id_guest', 'country', 'league'], 
    columns='bookmaker', 
    values=['1', 'X', '2', '1X', '12', 'X2', 'goals_threshold', '+', '-', 'J', 'N']
)
df.columns = df.columns.to_series().str.join("_")
df.reset_index(inplace=True)
df.fillna(value=1, inplace=True)


# df.to_excel("combined_odds.xlsx", index=False)




# 1, X, 2
# 1, X2
# X, 12
# 1X, 2
combinations = itertools.product(
    df.columns[df.columns.str.startswith("1_")],
    df.columns[df.columns.str.startswith("X_")],
    df.columns[df.columns.str.startswith("2_")],
)
[print(combination) for combination in combinations]
combinations = [list(combination) for combination in combinations]



def calc_combination(df: pd.DataFrame, combination: list):
    return ((1 / df[combination]).sum(axis = 1).rename('combination:' + str('&').join(combination)))




arbitrage_markets = [
    ["1", "X", "2"],
    ["1", "X2"],
    ["X", "12"],
    ["1X", "2"]
]

combinations_per_market = [itertools.product(*[df.columns[df.columns.str.startswith(item + "_")] for item in arbitrage_market]) for arbitrage_market in arbitrage_markets]
combinations = [[list(combination) for combination in combinations] for combinations in combinations_per_market]
combinations = itertools.chain.from_iterable(combinations) # or nested list comprehension


df_combinations = [calc_combination(df, combination) for combination in combinations]
df = pd.concat([df, *df_combinations], axis=1)

b = df.melt(id_vars=['date', 'id_home', 'id_guest', 'country', 'league'], value_vars=df.columns[df.columns.str.startswith("combination")], var_name="combination")
b.sort_values("value", ascending=True)






df_teams = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vSe3KOFay3lo9mz9WHY7ZUGwNcEQgpsFqw8CiGoTehpLMAMdkUhnEDV3t5zrQ6vNgaRW0v9E0lhBlak/pub?gid=1018777580&single=true&output=csv')
df_teams


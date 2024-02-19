import pandas as pd
import numpy as np


from datetime import datetime, date
import itertools
import re
import sys
sys.path.append("src")

from database import odds_collection

class OddsAnalyzer():
    def __init__(self) -> None:
        pass

    def analyze(self):
        odds = odds_collection.find({"date": {"$gte": datetime.today()}})
        
        df = pd.DataFrame.from_records(odds)
     
        df.sort_values(by='date_parsed', inplace=True)
        df = df.groupby(by=['date', 'sports', 'country', 'league', 'bookmaker', 'id_home', 'id_guest', 'team_home', 'team_guest'], as_index=False).last()

        df = df.pivot(
            index=['date', 'sports', 'country', 'league', 'id_home', 'id_guest', 'team_home', 'team_guest'], 
            columns='bookmaker', 
            values=['1', 'X', '2', '1X', '12', 'X2', 'J', 'N']
        )
        
        df.columns = df.columns.to_series().str.join("_")
        df.reset_index(inplace=True)
        df.fillna(value=1, inplace=True)



        def calc_combination(df: pd.DataFrame, combination: list):            
            return ((1 / df[combination]).sum(axis = 1).rename('combination: ' + str(' & ').join(combination)))




        arbitrage_markets = [
            ["1", "X", "2"],
            ["1", "X2"],
            ["X", "12"],
            ["1X", "2"],
            ["J", "N"]
        ]

        combinations_per_market = [itertools.product(*[df.columns[df.columns.str.startswith(item + "_")] for item in arbitrage_market]) for arbitrage_market in arbitrage_markets]
        combinations = [[list(combination) for combination in combinations] for combinations in combinations_per_market]
        combinations = itertools.chain.from_iterable(combinations) # or nested list comprehension


        df_combinations = [calc_combination(df, combination) for combination in combinations]
        df = pd.concat([df, *df_combinations], axis=1)

        b = df.melt(
            # id_vars=['date', 'id_home', 'id_guest', 'team_home', 'team_guest', 'sports', 'country', 'league'], 
            id_vars=df.columns[~df.columns.str.startswith("combination")],
            value_vars=df.columns[df.columns.str.startswith("combination")], 
            var_name="combination"
        )

        def extract_odds(row):
            return str("; ").join(row[row['combination'].replace("combination: ", "").split(" & ")].astype('string'))

        b['combination_odds'] = b.apply(extract_odds, axis=1)
        
        return b.sort_values("value", ascending=True)
        
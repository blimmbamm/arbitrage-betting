from abc import ABC, abstractmethod
from typing import List
import pandas as pd
from pandas.core.api import DataFrame as DataFrame
from datetime import datetime
from unidecode import unidecode

from datetime import date

import math


from config import Config
from database import teams, odds_collection



class BettingParser(ABC):

    __MARKETS = [
        {
            'bookmaker': 'bet3000',
            'sports': 'fussball',
            'markets': [
                {
                    'market_description': 'Standard',
                    'market': '0: Object',
                    'relevant_indices': [0, 2, 3, 5, 7, 9],
                    'headers': ["date", "home", "guest", "1", "X", "2"]
                },
                {
                    'market_description': 'Doppelte Chance',
                    'market': '3: Object',
                    'relevant_indices': [0, 2, 3, 5, 7, 9],
                    'headers': ["date", "home", "guest", "1X", "12", "X2"]
                },
                {
                    'market_description': 'Beide Teams treffen',
                    'market': '4: Object',
                    'relevant_indices': [0, 2, 3, 5, 7],
                    'headers': ["date", "home", "guest", "J", "N"]
                }
            ]
        },
        {
            'bookmaker': 'bet3000',
            'sports': 'eishockey',
            'markets': [
                {
                    'market_description': 'Standard',
                    'market': '0: Object',
                    'relevant_indices': [0, 2, 3, 5, 7, 9],
                    'headers': ["date", "home", "guest", "1", "X", "2"]
                },
                {
                    'market_description': 'Doppelte Chance',
                    'market': '3: Object',
                    'relevant_indices': [0, 2, 3, 5, 7, 9],
                    'headers': ["date", "home", "guest", "1X", "12", "X2"]
                },
                {
                    'market_description': 'Beide Teams treffen',
                    'market': '4: Object',
                    'relevant_indices': [0, 2, 3, 5, 7],
                    'headers': ["date", "home", "guest", "J", "N"]
                }
            ]
        },
        {
            'bookmaker': 'tipico',
            'sports': 'fussball',
            'markets': [
                {'name': 'standard', 'headers': ["1", "X", "2"]}, 
                {'name': 'double-chance', 'headers': ["1X", "12", "X2"]},
                {'name': 'score-both', 'headers': ["J", "N"]}
            ]   
        },
        {
            'bookmaker': 'tipwin',
            'sports': 'fussball',
            'markets': [
                {
                    'market_description': 'Standard',
                    'market': '3way',
                    'relevant_indices': [0, 2, 3, 4, 5, 6],
                    'headers': ["date", "home", "guest", "1", "X", "2"]
                },
                {
                    'market_description': 'double chance',
                    'market': 'double-chance',
                    'relevant_indices': [0, 2, 3, 4, 5, 6],
                    'headers': ["date", "home", "guest", "1X", "12", "X2"]
                },
                {
                    'market_description': 'Treffen beide teams',
                    'market': 'will-both-teams-score',
                    'relevant_indices': [0, 2, 3, 4, 5],
                    'headers': ["date", "home", "guest", "J", "N"]
                },                
            ]
        },
        {
            'bookmaker': 'winamax',
            'sports': 'fussball',
            'markets': [
                {
                    'market_description': 'Standard',
                    'market_level_1': 'Resultat',
                    'market_level_2': 'Ergebnis',
                    'relevant_indices': [0, 1, 2, 5, 7, 9],
                    'headers': ["date", "home", "guest", "1", "X", "2"]
                },
                {
                    'market_description': 'double chance',
                    'market_level_1': 'Resultat',
                    'market_level_2': 'Doppelte Chance',
                    'relevant_indices': [0, 1, 2, 5, 7, 9],
                    'headers': ["date", "home", "guest", "1X", "12", "X2"]
                },
                {
                    'market_description': 'Treffen beide teams',
                    'market_level_1': 'Tore pro Team',
                    'market_level_2': 'Schießen beide Mannschaften ein Tor?',
                    'relevant_indices': [0, 1, 2, 5, 7],
                    'headers': ["date", "home", "guest", "J", "N"]
                },                
            ]
        }
    ]

    markets: dict

    def __init__(self, bookmaker) -> None:
        super().__init__()
        # Do some general initialization here, e.g. load team names mapping, connect to database, etc.
        # self.markets = [market for market in self.__MARKETS if (market['bookmaker'] == bookmaker)]
        self.markets = {market['sports']: market['markets'] for market in self.__MARKETS if market['bookmaker'] == bookmaker}

    @abstractmethod
    def date_string_to_date(self, date_string: str) -> date:
        pass

    @abstractmethod
    def parse_single(self, config: Config, only_teams: bool = False) -> pd.DataFrame:
        pass

    @abstractmethod
    def parse(self, configs: List[Config], only_teams: bool = False) -> List[pd.DataFrame]:
        pass


    @abstractmethod
    def parse_market(self, market) -> pd.DataFrame:
        pass

    def parse_markets(self, config: Config, only_teams: bool = False) -> pd.DataFrame:
        
        # If only teams, then just first market:        
        # markets = self.markets[config.sports][:1] if only_teams else self.markets[config.sports]
        markets = self.get_markets(config=config, only_teams=only_teams)

        
        df = pd.concat([self.parse_market(market).set_index(['date', 'home', 'guest']) for market in markets], axis=1).reset_index(drop=False)

        df['date'] = pd.to_datetime(df['date'].str.strip().apply(self.date_string_to_date))
        df = self.add_additional_information(df, config=config)
        df = self.normalize_team_names(df)
        return df


    def get_markets(self, config: Config, only_teams: bool = False) -> list:
        return self.markets[config.sports][:1] if only_teams else self.markets[config.sports]


    
    def parse_teams(self, configs: List[Config]) -> List[pd.DataFrame]:
        return [df.melt(id_vars=['sports', 'country', 'league'], value_vars=['home', 'guest'], value_name='team', var_name='variable') \
            .drop(columns='variable') \
            .drop_duplicates() \
            .reset_index(drop=True) for df in self.parse(configs=configs, only_teams=True)]
        

    def add_additional_information(self, df: pd.DataFrame, config: Config):
        df['bookmaker'] = config.bookmaker
        df['sports'] = config.sports
        df['country'] = config.country
        df['league'] = config.league
        df['date_parsed'] = pd.to_datetime(datetime.today())
        return df
    
    def normalize_team_names(self, df: pd.DataFrame) -> pd.DataFrame:
        df['home'] = df['home'].apply(unidecode)
        df['guest'] = df['guest'].apply(unidecode)
        return df
    
    def push_teams_to_google_sheets(self, dfs_teams: List[pd.DataFrame]):
        teams.clear_basic_filter()
        
        df_teams_db = pd.DataFrame.from_records(teams.get_all_records()).drop(columns='action_needed', errors='ignore')
        teams_db = df_teams_db[['sports', 'country', 'league']].drop_duplicates().values.tolist()

        def process_team(df_teams: pd.DataFrame) -> pd.DataFrame:
            team = df_teams.iloc[0, :].tolist()[:-1]
            if team in teams_db:
                # add existing id if possible, leave empty else
                return df_teams.join(df_teams_db.set_index(['sports', 'country', 'league', 'team']), on=['sports', 'country', 'league', 'team'])
            else:
                # add everything and also add id already
                return df_teams.reset_index(drop=False).rename(columns={'index': 'id'})
                

        dfs_teams = [process_team(df_team) for df_team in dfs_teams]
        df_teams_db_updated = pd.concat([df_teams_db, *dfs_teams]).drop_duplicates().sort_values(by=['sports', 'country', 'league', 'team']).reset_index(drop=True)


        df_action_needed = df_teams_db_updated[df_teams_db_updated['id'].isna()][['sports', 'country', 'league']].drop_duplicates().set_index(['sports', 'country', 'league'], drop=True)
        df_action_needed['action_needed'] = 1

        df_teams_db_updated = df_teams_db_updated.join(df_action_needed, on=['sports', 'country', 'league']).fillna({'action_needed': 0})
        df_teams_db_updated = df_teams_db_updated[['sports', 'country', 'league', 'team', 'action_needed', 'id']]

        list_teams_db_updated = df_teams_db_updated.values.tolist()



        list_teams_db_updated = [row[:-1] if math.isnan(row[-1]) else row for row in list_teams_db_updated]

        teams.clear()
        teams.update([df_teams_db_updated.columns.values.tolist()] + list_teams_db_updated)
        teams.set_basic_filter(1, 1, len(df_teams_db_updated) + 1, 6)

    @staticmethod
    def update_teams_mapping():
        df_teams = pd.DataFrame.from_records(teams.get_all_records())
        if any(df_teams.id.isna()):
            print("Some IDs are missing, update first")
            return
        
        # All teams with all variants:
        df_teams.drop(columns='action_needed').to_csv("teams_mapping.csv", index=False)

        # Unique teams for joining back later
        df_teams.groupby(by=['sports', 'country', 'league', 'id']).agg({'team': 'first'}).reset_index().to_csv('teams_mapping_unique.csv', index=False)

        print('Updated teams mapping tables')


    @staticmethod
    def normalize(df: pd.DataFrame) -> pd.DataFrame:
        # df = results[0]
        # df = pd.DataFrame()
        df_teams_mapping = pd.read_csv('teams_mapping.csv')
        df = df.join(df_teams_mapping.set_index(['sports', 'country', 'league', 'team'], drop=True).rename(columns={'id': 'id_home'}), on=['sports', 'country', 'league', 'home'])
        df = df.join(df_teams_mapping.set_index(['sports', 'country', 'league', 'team'], drop=True).rename(columns={'id': 'id_guest'}), on=['sports', 'country', 'league', 'guest'])

        df_teams_mapping_unique = pd.read_csv('teams_mapping_unique.csv').set_index(['sports', 'country', 'league', 'id'])
        
        df = df.join(df_teams_mapping_unique.rename(columns={'team': 'team_home'}), on=['sports', 'country', 'league', 'id_home'])
        df = df.join(df_teams_mapping_unique.rename(columns={'team': 'team_guest'}), on=['sports', 'country', 'league', 'id_guest'])


        df[['1', 'X', '2', '1X', '12', 'X2', 'J', 'N']] = df[['1', 'X', '2', '1X', '12', 'X2', 'J', 'N']] \
            .replace('', '1') \
            .apply(lambda col: col.astype('string')) \
            .apply(lambda col: col.str.replace(",", ".").astype('float'))
        return df


    @staticmethod
    def push_to_database(dfs_results: List[pd.DataFrame]):
        df = BettingParser.normalize(pd.concat(dfs_results, ignore_index=True))
        # dfs_results = [BettingParser.normalize(df_results) for df_results in dfs_results]
        return odds_collection.insert_many(df.to_dict('records'))

        



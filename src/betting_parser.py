from abc import ABC, abstractmethod
from typing import List
import pandas as pd
from pandas.core.api import DataFrame as DataFrame
from datetime import datetime


from config import Config


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
                    'relevant_indices': [0, 1, 2, 4, 6, 8],
                    'headers': ["date", "home", "guest", "1", "X", "2"]
                },
                {
                    'market_description': 'double chance',
                    'market_level_1': 'Resultat',
                    'market_level_2': 'Doppelte Chance',
                    'relevant_indices': [0, 1, 2, 4, 6, 8],
                    'headers': ["date", "home", "guest", "1X", "12", "X2"]
                },
                {
                    'market_description': 'Treffen beide teams',
                    'market_level_1': 'Tore pro Team',
                    'market_level_2': 'Schießen beide Mannschaften ein Tor?',
                    'relevant_indices': [0, 1, 2, 4, 6],
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
    def parse_single(self, config: Config) -> pd.DataFrame:
        pass

    @abstractmethod
    def parse(self, configs: List[Config], only_teams: bool = False) -> List[pd.DataFrame]:
        pass

    # @abstractmethod
    # def parse_teams(self, configs: List[Config]) -> pd.DataFrame:
    #     pass

    def get_markets(self, config: Config, only_teams: bool = False) -> list:
        return self.markets[config.sports][:1] if only_teams else self.markets[config.sports]

    def normalize(self):
        # e.g. ...join(self.df_teams)
        return "normalized"
    
    def parse_teams(self, configs: List[Config]) -> pd.DataFrame:
        return pd.concat(self.parse(configs=configs, only_teams=True), axis=0) \
            .melt(id_vars=['sports', 'country', 'league'], value_vars=['home', 'guest'], value_name='team', var_name='variable') \
            .drop(columns='variable') \
            .drop_duplicates()

    def add_additional_information(self, df: pd.DataFrame, config: Config):
        df['bookmaker'] = config.bookmaker
        df['sports'] = config.sports
        df['country'] = config.country
        df['league'] = config.league
        df['date_parsed'] = datetime.today()
        return df


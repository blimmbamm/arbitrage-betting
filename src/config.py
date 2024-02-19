from __future__ import annotations
from typing import List

import pandas as pd

from database import configs_collection


class Config:
    
    bookmaker: str
    sports: str
    country: str
    league: str
    config: dict
    

    def __init__(self, bookmaker, sports, country, league, config, _id = None) -> None:
        self.bookmaker = bookmaker
        self.sports = sports
        self.country = country
        self.league = league
        self.config = config
        if not _id is None:
            self._id = _id

    @classmethod
    def from_dict(cls, dict):
        return cls(**dict)
    
    @classmethod
    def get_configs(cls, query):
        configs = configs_collection.find(query)
        return [cls(**config) for config in configs]
    
    @staticmethod
    def insert_config(config: Config):
        return configs_collection.insert_one(vars(config))
    
    def insert_config(self):
        return configs_collection.insert_one(vars(self))

    @staticmethod
    def insert_configs(configs: List[Config]):
        return configs_collection.insert_many([vars(config) for config in configs])

    @classmethod
    def from_csv(cls, csv_file: str) -> List[Config]:
        
        def reshape_config(row: pd.Series):
            columns = row.index[row.index.str.startswith('config')].str.replace(pat='config_', repl='')
            values = row[row.index.str.startswith('config')]
            return dict(zip(columns, values))

        
        df = pd.read_csv(csv_file, sep=";")
        df['config'] = df.apply(reshape_config, axis=1)
        df = df.loc[:, ~df.columns.str.contains('config_')]
                   

        return [cls(**config) for config in df.to_dict('records')]


    

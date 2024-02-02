from pandas.core.api import DataFrame as DataFrame
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import itertools
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from datetime import datetime, timedelta, date


class Bet3000Parser:

    driver: webdriver.Chrome

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)        

        self.driver.get('https://bet3000.de/sports')

        self.driver.find_element(By.ID, value="onetrust-accept-btn-handler").click()

        self.driver.set_window_size(width=1100, height=800)
        print('Parser ready')

    def date_string_to_date(self, date_string: str):
        today = date.today()
        weekday_dict = {'Montag': 0, 'Dienstag': 1, 'Mittwoch': 2 , 'Donnerstag':3 , 'Freitag': 4, 'Samstag': 5, 'Sonntag': 6,
                        'Mo': 0, 'Di': 1, 'Mi': 2, 'Do': 3, 'Fr': 4, 'Sa': 5, 'So': 6}
        
        if date_string.lower() == "heute":
            return today
        elif date_string.lower() == "morgen":
            return today + timedelta(days=1)
        elif date_string in weekday_dict.keys():
            return today + timedelta(days=(weekday_dict[date_string] - today.weekday()) % 7)
        else:
            return datetime.strptime(f"{date_string}-{today.year}", '%d-%m-%Y').date()
    
    def get_elements_text(self):
        return self.driver.find_element(By.CSS_SELECTOR, 'match-r [class*="match-row-container"]').text.split("\n")

    
    def parse(self, config, only_teams=False):
        self.refresh()

        sport_type_menu_items = self.driver.find_elements(By.CSS_SELECTOR, '[class*="sports-menu-item"]')
        sport_type_menu = sport_type_menu_items[[menu_item.text for menu_item in sport_type_menu_items].index(config['config']['sports'])]
        sport_type_menu.click()
        
        time.sleep(1)

        country_menu_items = self.driver.find_elements(By.CSS_SELECTOR, '[class*="sports-menu-dropdown"]')
        country_menu_items[[menu_item.text.split("\n")[0] for menu_item in country_menu_items].index(config['config']['country'])].click()

        time.sleep(1)

        league_menu_items = self.driver.find_elements(By.CSS_SELECTOR, '[class*="menu-content-item"]')
        league_menu_items[[menu_item.text.split("\n")[0] for menu_item in league_menu_items].index(config['config']['league'])].click()

        time.sleep(1)

        markets = MARKETS[config['sports']][:1] if only_teams else MARKETS[config['sports']]
        
        df = pd.concat([self.parse_market(market).set_index(['date', 'home', 'guest']) for market in markets], axis=1).reset_index(drop=False)
        df['sports'] = config['sports']
        df['country'] = config['country']
        df['league'] = config['league']
        df['date_parsed'] = datetime.today()
        df['date'] = df['date'].str.replace(pat=".", repl="").str.strip().apply(self.date_string_to_date)

        return df

    def parse_market(self, market):
        select = Select(self.driver.find_element(By.CSS_SELECTOR, '[class*="odd-combo-row"] select'))
        select.select_by_value(market['market'])

        time.sleep(1)
        
        def extract_data(items: list):
            items.extend(itertools.repeat(pd.NA, 1 + max(market['relevant_indices']) - len(items)))
            return np.array(items)[market['relevant_indices']]
        
        return pd.DataFrame.from_records([dict(zip(
            market['headers'],
            extract_data(element.text.split('\n'))
        )) for element in self.driver.find_elements(By.CSS_SELECTOR, 'match-r [class*="match-row-container"]')])
        

    def refresh(self):
        self.driver.refresh()
        time.sleep(1)


    def parse_multiple(self, configs, only_teams=False):
        def refresh_and_parse(config):
            self.refresh()
            return self.parse(config, only_teams=only_teams)
        
        return [refresh_and_parse(config) for config in configs]
    
    def parse_teams(self, configs):
        return pd.concat(self.parse_multiple(configs=configs, only_teams=True), axis=0) \
            .melt(id_vars=['sports', 'country', 'league'], value_vars=['home', 'guest'], value_name='team', var_name='variable') \
            .drop(columns='variable') \
            .drop_duplicates()


CONFIG = [
    {'bookmaker': 'tipico', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga'}},
    {'bookmaker': 'tipwin', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'sports': 'Fussball', 'country': 'Spanien', 'league': 'La Liga'}},
    {'bookmaker': 'winamax', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'url': 'https://www.winamax.de/sportwetten/sports/1/32/36'}},
    {'bookmaker': 'bet3000', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'sports': 'Fußball', 'country': 'Spanien', 'league': 'La Liga'}},
    {'bookmaker': 'bet3000', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga-2', 'config': {'sports': 'Fußball', 'country': 'Spanien', 'league': 'La Liga 2'}},
    {'bookmaker': 'bet3000', 'sports': 'eishockey', 'country': 'schweden', 'league': 'shl', 'config': {'sports': 'Eishockey', 'country': 'Schweden', 'league': 'SHL'}}
]

MARKETS = {
    'fussball': [
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
    ], 
    'eishockey': [
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
    ],
    'handball': []
}

parser = Bet3000Parser()
results = parser.parse(CONFIG[3])
parser.refresh()
results = parser.parse_multiple(CONFIG[3:])
[dict(result) for result in results[0]]

parser.parse_teams(CONFIG[5:])

parser.parse(CONFIG[5])

parser.get_elements_text()
from datetime import date
date.today()




from abc import ABC, abstractmethod
from typing import List

class Config:
    pass

class Parser(ABC):

    def __init__(self) -> None:
        super().__init__()
        # Do some general initialization here, e.g. load team names mapping, connect to database, etc.

    @abstractmethod
    def parse(self, config: Config) -> pd.DataFrame:
        pass

    @abstractmethod
    def parse_multiple(self, configs: List[Config], only_teams: bool = False) -> List[pd.DataFrame]:
        pass

    @abstractmethod
    def parse_teams(self, configs: List[Config]) -> pd.DataFrame:
        pass




    def normalize(self):
        # e.g. ...join(self.df_teams)
        return "normalized"
    

class SomeParser(Parser):
    def parse(config) -> DataFrame:
        return super().parse()
    
    def parse_multiple(self, configs: List[Config], only_teams: bool = False) -> List[DataFrame]:
        return super().parse_multiple(configs, only_teams)
    
    
class SomeOtherParser(Parser):
    def some_other_function():
        pass

a = SomeParser()
b = SomeOtherParser()






class ParentClass:
    def __init__(self) -> None:
        pass

    def some_function(self, a: float, b: float, c: float) -> float:
        return a + b + c
    
    def other_function(self, x):
        return x**2
    

class ChildClass(ParentClass):
    def __init__(self) -> None:
        super().__init__()

    def some_function(self, a: float, b: float, c: float) -> float:
        return "asdf"

    def some_child_function(x):
        x+=1
        return super().other_function(x)


dingens = ChildClass()
dingens.other_function(5)
from typing import List
from pandas.core.api import DataFrame as DataFrame
from betting_parser import BettingParser
from config import Config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import time
import itertools
import numpy as np
import pandas as pd
from re import sub
from datetime import date, timedelta, datetime

sub(pattern=r"\w{2} ", repl="", string="Fr 09.02.")
class TipwinParser(BettingParser):

    driver: webdriver.Chrome

    def __init__(self) -> None:
        super().__init__(bookmaker='tipwin')
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(width=1150, height=800)
        self.driver.get('https://www.tipwin.de/de/sports/full')
        self.driver.implicitly_wait(30)
        self.driver.find_element(By.CSS_SELECTOR, '[class*="popup__card"] button').click()
        self.driver.implicitly_wait(0.5)
        print("Parser ready")

    def refresh(self):
        self.driver.get('https://www.tipwin.de/de/sports/full')
        time.sleep(1)

    def date_string_to_date(self, date_string: str):
        if date_string == "Heute":
            return date.today()
        elif date_string == "Mrg":
            return date.today() + timedelta(days=1)
        else:
            return datetime.strptime(f"{sub(pattern=r"\w{2} ", repl="", string=date_string)}{date.today().year}", '%d.%m.%Y').date()


    def parse_market(self, market):
        select = Select(self.driver.find_element(By.CSS_SELECTOR, '[class*="offer__type__select"]'))
        select.select_by_value(market['market'])

        time.sleep(1)

        def extract_data(items: list):
            try:
                items.pop(items.index('LIVE'))
            except:
                pass

            items.extend(itertools.repeat(pd.NA, 1 + max(market['relevant_indices']) - len(items)))
            return np.array(items)[market['relevant_indices']]
        
        return pd.DataFrame.from_records([dict(zip(
            market['headers'],
            extract_data(element.text.split('\n'))
        )) for element in self.driver.find_elements(By.CSS_SELECTOR, '[class*="offer__body__row"]')])


    def parse_single(self, config: Config, only_teams: bool = False) -> DataFrame:
        
        # Select sport in sports menu:
        # Fussball seems to be default selection, hence only select sports if not fussball:
        if config.sports != "fussball":
            sports_menu_index = [element.text for element in self.driver.find_elements(By.CSS_SELECTOR, '[class*="nav--secondary__title"]')].index(config.config['sports'])
            self.driver.find_elements(By.CSS_SELECTOR, '[class*="nav--secondary__title"]')[sports_menu_index].click()

        # Select country in country menu:
        country_menu_index = [element.text for element in self.driver.find_elements(By.CSS_SELECTOR, '[class*="nav--tertiary__title"]')].index(config.config['country'])
        self.driver.find_elements(By.CSS_SELECTOR, '[class*="nav--tertiary__title"]')[country_menu_index].click()

        # Select league
        league_menu_index = [element.text for element in self.driver.find_elements(By.CSS_SELECTOR, '[class*="nav--quaternary__link"] label')].index(config.config['league'])
        self.driver.find_elements(By.CSS_SELECTOR, '[class*="nav--quaternary__link"] label')[league_menu_index].click()

        markets = self.get_markets(config=config, only_teams=only_teams)

        # [self.parse_market(market) for market in markets]
        df = pd.concat([self.parse_market(market).set_index(['date', 'home', 'guest']) for market in markets], axis=1).reset_index(drop=False)
        
        df['date'] = df['date'].str.strip().apply(self.date_string_to_date)

        return self.add_additional_information(df, config=config)

    
    def parse(self, configs: List[Config], only_teams: bool = False) -> List[DataFrame]:
        def refresh_and_parse(config: Config):
            self.refresh()
            return self.parse_single(config, only_teams=only_teams)
        
        return [refresh_and_parse(config) for config in configs]
    
    def get_elements_text(self):
        return self.driver.find_element(By.CSS_SELECTOR, '[class*="offer__body__row"]').text.split("\n")
    



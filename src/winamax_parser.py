from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from pandas.core.api import DataFrame as DataFrame
from betting_parser import BettingParser
from config import Config
import time
import pandas as pd
import itertools
import numpy as np
from datetime import date, datetime, timedelta
import locale

class WinamaxParser(BettingParser):

    def __init__(self) -> None:
        super().__init__(bookmaker='winamax')

        locale.setlocale(locale.LC_ALL, 'de_DE')

        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(2)
        # self.driver.set_window_size(1000, 800)
        self.driver.maximize_window()

        # Call landing page to deny cookies etc.:
        # self.driver.get('https://www.winamax.de/sportwetten/')
        
        # self.driver.find_element(By.CSS_SELECTOR, '[data-testid="overlay"]').find_element(By.XPATH, value="./..").find_element(By.TAG_NAME, "button").click()
        # self.close_overlays()
        print("Parser ready")

    def close_overlays(self):
        try: 
            self.driver.find_element(By.ID, value="tarteaucitronAllDenied2").click()
        except:
            pass
        self.driver.find_element(By.CSS_SELECTOR, '[data-testid="overlay"]').find_element(By.XPATH, value="./..").find_element(By.TAG_NAME, "button").click()

    def date_string_to_date(self, date_string) -> date:
        today = date.today()
        weekday_dict = {'montag': 0, 'dienstag': 1, 'mittwoch': 2 , 'donnerstag':3 , 'freitag': 4, 'samstag': 5, 'sonntag': 6}
        
        if date_string == "heute":                       
            return today
        elif date_string == "morgen":
            return today + timedelta(days=1)    
        elif date_string in weekday_dict.keys():
            return today + timedelta(days=(weekday_dict[date_string] - today.weekday()) % 7)
        else:    
            return datetime.strptime(date_string, '%d %b %Y').date()
        

    def parse_single(self, config: Config, only_teams: bool = False) -> DataFrame:

        self.driver.get(config.config['url'])

        time.sleep(1)

        self.close_overlays()

        markets = self.get_markets(config=config, only_teams=only_teams)

        df = pd.concat([self.parse_market(market).set_index(['date', 'home', 'guest']) for market in markets], axis=1).reset_index(drop=False)

        # df[["date", "time"]] = df["datetime"].str.extract(pat=r"(.*) um (\d{2}:\d{2})", expand=True)
        df['date'] = df['date'].str.extract(pat=r"(.*) um", expand=False).str.lower().str.strip().apply(self.date_string_to_date)
        return self.add_additional_information(df, config=config)

        

    def parse_market(self, market):
        # Open menu for type of market:
        self.driver.find_element(By.CSS_SELECTOR, '[class*="selector-button"]').click()

        time.sleep(1)

        # Choose e.g. Resultat (index-based):
        index = [element.text for element in self.driver.find_elements(By.CSS_SELECTOR, '[class*="selector-list"] > p')].index(market['market_level_1'])
        self.driver.find_elements(By.CSS_SELECTOR, '[class*="selector-list"] > p')[index].click()
        
        time.sleep(1)

        # Open menu for actual market selection:
        self.driver.find_elements(By.CSS_SELECTOR, '[class*="selector-button"]')[1].click()

        time.sleep(1)

        # Choose some market, e.g. Endergebnis:
        index = [element.text for element in self.driver.find_elements(By.CSS_SELECTOR, '[class*="selector-list"] > p')].index(market['market_level_2'])
        self.driver.find_elements(By.CSS_SELECTOR, '[class*="selector-list"] > p')[index].click()

        time.sleep(1)

        # matches = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid*="match-card"]')

        def extract_data(items: list):
            # Remove '-', '%', 'LIVE':
            items = [item for item in items if not any([pattern in item for pattern in ["-", "%", "LIVE"]])]
            
            # Fill up NAs at the end:
            items.extend(itertools.repeat(pd.NA, 1 + max(market['relevant_indices']) - len(items)))

            return np.array(items)[market['relevant_indices']]

        return pd.DataFrame.from_records([dict(zip(
            market['headers'],
            extract_data(element.text.split('\n'))
        )) for element in self.driver.find_elements(By.CSS_SELECTOR, '[data-testid*="match-card"]')])
    
    def parse(self, configs: List[Config], only_teams: bool = False) -> List[DataFrame]:
        return [self.parse_single(config, only_teams=only_teams) for config in configs]
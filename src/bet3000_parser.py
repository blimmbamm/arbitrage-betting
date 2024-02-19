from typing import List
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from pandas.core.api import DataFrame as DataFrame
import pandas as pd
import numpy as np


import itertools
import time
from datetime import datetime, timedelta, date


from betting_parser import BettingParser
from config import Config


class Bet3000Parser(BettingParser):

    driver: webdriver.Chrome
    
    def __init__(self):
        super().__init__('bet3000')
        self.driver = webdriver.Chrome()
        # self.driver.implicitly_wait(5)        

        self.driver.get('https://bet3000.de/sports')

        time.sleep(5)

        self.driver.find_element(By.ID, value="onetrust-accept-btn-handler").click()

        self.driver.set_window_size(width=1100, height=800)
        print('Parser ready')

    
    def date_string_to_date(self, date_string: str) -> date:
        date_string = date_string.replace(".", "")
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

    
    def parse_single(self, config: Config, only_teams: bool = False) -> DataFrame:
        # self.refresh()
        sleep_duration = 0.5

        sport_type_menu_items = self.driver.find_elements(By.CSS_SELECTOR, '[class*="sports-menu-item"]')
        sport_type_menu = sport_type_menu_items[[menu_item.text for menu_item in sport_type_menu_items].index(config.config['sports'])]
        sport_type_menu.click()
        
        time.sleep(sleep_duration)

        country_menu_items = self.driver.find_elements(By.CSS_SELECTOR, '[class*="sports-menu-dropdown"]')
        country_menu_items[[menu_item.text.split("\n")[0] for menu_item in country_menu_items].index(config.config['country'])].click()

        time.sleep(sleep_duration)

        league_menu_items = self.driver.find_elements(By.CSS_SELECTOR, '[class*="menu-content-item"]')
        league_menu_items[[menu_item.text.split("\n")[0] for menu_item in league_menu_items].index(config.config['league'])].click()

        time.sleep(sleep_duration)

        return self.parse_markets(config=config, only_teams=only_teams)

    
    def parse(self, configs: List[Config], only_teams: bool = False) -> List[DataFrame]:
        def refresh_and_parse(config: Config):
            self.refresh()
            return self.parse_single(config, only_teams=only_teams)
        
        return [refresh_and_parse(config) for config in configs]
       

    def parse_market(self, market):
        select = Select(self.driver.find_element(By.CSS_SELECTOR, '[class*="odd-combo-row"] select'))
        select.select_by_value(market['market'])

        time.sleep(0.5)
        
        def extract_data(items: list):
            items.extend(itertools.repeat(pd.NA, 1 + max(market['relevant_indices']) - len(items)))
            return np.array(items)[market['relevant_indices']]
        
        return pd.DataFrame.from_records([dict(zip(
            market['headers'],
            extract_data(element.text.split('\n'))
        )) for element in self.driver.find_elements(By.CSS_SELECTOR, 'match-r [class*="match-row-container"]')])
        

    def refresh(self):
        self.driver.refresh()
        # time.sleep(1)
    
    

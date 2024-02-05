from typing import List
from pandas.core.api import DataFrame as DataFrame
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import pandas as pd
import time
from datetime import datetime
from config import Config

# from util import normalize_data
from betting_parser import BettingParser



class TipicoParser(BettingParser):
    
    driver: webdriver.Chrome
    
    def __init__(self):
        super().__init__(bookmaker='tipico')
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)
        self.driver.set_window_size(width=1000, height=800)
        self.driver.get('https://sports.tipico.de/')
        self.driver.find_element(By.ID, '_evidon-accept-button').click()
        self.driver.implicitly_wait(0)
        
        # try:
        #     self.driver.find_element(By.ID, '_evidon-accept-button').click()
        # except:
        #     pass
        print('Parser ready')
    

    def parse_single(self, config: Config, only_teams: bool = False) -> DataFrame:
        # 1. Navigieren
        self.driver.get(f'https://sports.tipico.de/de/alle/{config.sports}/{config.country}/{config.league}')
                      
        time.sleep(1)

        # 2. im zweiten Market z.b. head-to-head auswaehlen:
        try:
            select = Select(self.driver.find_elements(By.CSS_SELECTOR, '[testid="Program_SELECTION"] select')[1])    
            select.select_by_value('head-to-head')
            time.sleep(1)
        except:
            pass

        # 4. market config durchlaufen   
        # markets = self.markets[config.sports][:1] if only_teams else self.markets[config.sports]
        markets = self.get_markets(config=config, only_teams=only_teams)
        
        df = pd.concat([self.parse_market(market).set_index(['date', 'home', 'guest']) for market in markets], axis=1) \
            .reset_index(inplace=False)
        # markets = [market_odds.set_index(['date', 'home', 'guest']) for market_odds in markets_odds]

        # df = pd.concat(markets, axis=1).reset_index(inplace=False)
        df["date"] = df["date"].str.replace(pat=r"\w*, ", repl="", regex=True) \
            .str.replace(pat="Heute", repl=datetime.today().strftime(r"%d.%m")) \
            .apply(lambda value: datetime.strptime(value + "." + str(datetime.today().year), "%d.%m.%Y").date())        
        
        return self.add_additional_information(df, config)
    


    def parse_event(self, event_element, odds_headers):
        if event_element.tag_name == 'div':
            return {'date': event_element.text}
        else:
            teams = dict(zip(['home', 'guest'], [team_element.text for team_element in event_element.find_elements(By.CSS_SELECTOR, '[data-gtmid="teamNames"] span')]))

            odds_group_element = event_element.find_element(By.CSS_SELECTOR, '[data-testid="odd-groups"]')
            
            odds = dict(zip(odds_headers, [
                *[fixed_element.text for fixed_element in event_element.find_elements(By.CSS_SELECTOR, '[class*="fixed-param-texts"]')],
                *[span.text for span in odds_group_element.find_elements(By.TAG_NAME, "span")]
            ]))
            
            return {**teams, **odds}
        

    def parse_market(self, market_config) -> pd.DataFrame:
        
        select_element = self.driver.find_element(By.CSS_SELECTOR, '[class="SportHeader-styles-module-drop-down"]')
        select = Select(select_element)
        select.select_by_value(market_config['name'])

        time.sleep(1)

        elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="competition-events"] > *')

        raw_results = [self.parse_event(element, odds_headers=market_config['headers']) for element in elements]

        results = []

        date = raw_results[0]
        for raw_result in raw_results:
            if len(raw_result) > 1:
                results.append({**date, **raw_result})
            else:
                date = raw_result

        return pd.DataFrame.from_records(results)

    def parse(self, configs: List[Config], only_teams: bool = False) -> List[DataFrame]:
        return [self.parse_single(config=config, only_teams=only_teams) for config in configs]


        
        

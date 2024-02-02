from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import pandas as pd
import time
from datetime import datetime

from util import normalize_data



class TipicoParser():
    
    driver: webdriver.Chrome
    
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(width=1000, height=800)
    
    
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
        

    def parse_market(self, market_config):
        
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




    def parse_tipico(self, country, league, markets, normalize=True):
        # 1. Navigieren
        # country = 'spanien'
        # league = 'la-liga'
        self.driver.get('https://sports.tipico.de/de/alle/fussball/' + country + '/' + league)
        
        time.sleep(1)
        try:
            self.driver.find_element(By.ID, '_evidon-accept-button').click()
        except:
            pass
        
        # 2. Groesse aendern s.d. nur zwei Markets angezeigt sind
        
        time.sleep(0.5)

        # 3. im zweiten Market z.b. head-to-head auswaehlen:
        try:
            select = Select(self.driver.find_elements(By.CSS_SELECTOR, '[testid="Program_SELECTION"] select')[1])    
            select.select_by_value('head-to-head')
        except:
            pass

        time.sleep(1)
        # 4. market config durchlaufen    
        
        markets_odds = [self.parse_market(market_config, self.driver) for market_config in markets]
        markets = [market_odds.set_index(['date', 'home', 'guest']) for market_odds in markets_odds]

        df = pd.concat(markets, axis=1).reset_index(inplace=False)
        df["date"] = df["date"].str.replace(pat=r"\w*, ", repl="", regex=True) \
            .str.replace(pat="Heute", repl=datetime.today().strftime(r"%d.%m")) \
            .apply(lambda value: value + "." + str(datetime.today().year))
        df["country"] = country
        df["league"] = league.replace("-", "_")
        df["bookmaker"] = "tipico"
        
        if normalize:
            return normalize_data(df)
        else:
            return df
        
    def parse_teams(self, country, league, driver):
        df = self.parse_tipico(country=country, league=league, markets=MARKETS[:1], driver=driver, normalize=False)
        # return df.melt(value_vars=['home', 'guest'], var_name='var', value_name='team').drop(columns='var').drop_duplicates()
        return df.melt(id_vars=['country', 'league'], value_vars=['home', 'guest'], var_name='var', value_name='team').drop(columns='var').drop_duplicates()
        
        

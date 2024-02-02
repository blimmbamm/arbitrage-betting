from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
import pandas as pd
import time
from datetime import datetime, timedelta
import locale
import numpy as np
import re

locale.setlocale(locale.LC_ALL, 'de_DE')
# locale.setlocale(locale.LC_ALL, 'en_US')

driver = webdriver.Chrome()
# driver.implicitly_wait(1)


driver.get('https://www.winamax.de/sportwetten/sports/1/32/37')
driver.find_element(By.ID, value="tarteaucitronAllDenied2").click()
# driver.find_elements(By.TAG_NAME, "button")
driver.set_window_size(1920, 1080)
# driver.set_window_position(0, 0)
driver.find_element(By.CSS_SELECTOR, '[data-testid="overlay"]').find_element(By.XPATH, value="./..").find_element(By.TAG_NAME, "button").click()

# Open menu for type of market:
driver.find_element(By.CSS_SELECTOR, '[class*="selector-button"]').click()

# Choose e.g. Resultat (index-based):
resultat_index = 0
driver.find_elements(By.CSS_SELECTOR, '[class*="selector-list"] > p')[4].click()

# Open menu for actual market selection:
driver.find_elements(By.CSS_SELECTOR, '[class*="selector-button"]')[1].click()

# Choose some market, e.g. Endergebnis:
endergebnis_index = 0
driver.find_elements(By.CSS_SELECTOR, '[class*="selector-list"] > p')[0].click()

matches = driver.find_elements(By.CSS_SELECTOR, '[data-testid*="match-card"]')
len(matches)
len(matches[0].text.split("\n"))
match_text = matches[0].text

[len(match.text.split("\n")) for match in matches]
relevant_indices = [0, 1, 2, 5, 7]
[extract_data(match.text, relevant_indices) for match in matches]




def extract_data(match_text, relevant_indices):
    # 1. split("\n")
    # 2. % und - entfernen
    # 3. relevante indices auswaehlen und zurueckgeben
    return np.array([item for item in match_text.split("\n") if not (item=="-" or "%" in item)])[relevant_indices]

def parse_market(market):

    # Open menu for type of market:
    driver.find_element(By.CSS_SELECTOR, '[class*="selector-button"]').click()
    time.sleep(0.5)

    # Choose e.g. Resultat (index-based):
    index = [item.text for item in driver.find_elements(By.CSS_SELECTOR, '[class*="selector-list"] > p')].index(market['market_type'])
    driver.find_elements(By.CSS_SELECTOR, '[class*="selector-list"] > p')[index].click()
    time.sleep(0.5)

    # Open menu for actual market selection:
    driver.find_elements(By.CSS_SELECTOR, '[class*="selector-button"]')[1].click()
    time.sleep(0.5)

    # Choose some market, e.g. Endergebnis:
    index = [item.text for item in driver.find_elements(By.CSS_SELECTOR, '[class*="selector-list"] > p')].index(market['market'])
    driver.find_elements(By.CSS_SELECTOR, '[class*="selector-list"] > p')[index].click()
    time.sleep(0.5)
    
    matches = driver.find_elements(By.CSS_SELECTOR, '[data-testid*="match-card"]')
    time.sleep(0.5)
      
    return pd.DataFrame.from_records(
        [dict(zip(
            market['headers'],
            extract_data(match.text, market['relevant_indices'])
        )) for match in matches]
    )


def date_string_to_date(date_string):
    today = datetime.today()
    weekday_dict = {'Montag': 0, 'Dienstag': 1, 'Mittwoch': 2 , 'Donnerstag':3 , 'Freitag': 4, 'Samstag': 5, 'Sonntag': 6}
    
    date = None
    if date_string == "heute":
        date = today
    elif date_string == "morgen":
        date = today + timedelta(days=1)    
    elif date_string in weekday_dict.keys():
        date = today + timedelta(days=(weekday_dict[date_string] - today.weekday()) % 7)
    else:    
        date = datetime.strptime(date_string, '%d %b %Y')
    
    return date.strftime(r"%d.%m.%Y")

def format_data(df: pd.DataFrame):
    df_copy = df.copy()
    df_copy[["date", "time"]] = df_copy["datetime"].str.extract(pat=r"(.*) um (\d{2}:\d{2})", expand=True)
    df_copy["date"] = df_copy["date"].apply(date_string_to_date)
    df_copy["date_parsed"] = datetime.now()

    return df_copy.drop(columns="datetime")




def parse_winamax(url):
    driver.get(url)

    try:
        driver.find_element(By.ID, value="tarteaucitronAllDenied2").click()
    except:
        pass
    # driver.find_elements(By.TAG_NAME, "button")
    driver.set_window_size(1920, 1080)
    # driver.set_window_position(0, 0)
    driver.find_element(By.CSS_SELECTOR, '[data-testid="overlay"]').find_element(By.XPATH, value="./..").find_element(By.TAG_NAME, "button").click()
    
    df_markets = pd.concat([parse_market(market).set_index(['datetime', 'home', 'guest']) for market in MARKETS], axis=1).reset_index(inplace=False)
    
    return format_data(df_markets)
    # return df_markets

MARKETS = [
    {
        'market_type': 'Resultat',
        'market': 'Ergebnis',
        'relevant_indices': [0, 1, 2, 5, 7, 9],
        'headers': ["datetime", "home", "guest", "1", "X", "2"]
    },
    {
        'market_type': 'Resultat',
        'market': 'Doppelte Chance',
        'relevant_indices': [0, 1, 2, 5, 7, 9],
        'headers': ["datetime", "home", "guest", "1X", "12", "X2"]
    },
    {
        'market_type': 'Tore pro Team',
        'market': 'Schießen beide Mannschaften ein Tor?',
        'relevant_indices': [0, 1, 2, 5, 7],
        'headers': ["datetime", "home", "guest", "J", "N"]
    }
]

config = [
    {'country': 'Spanien', 'league': 'La Liga', 'url': 'https://www.winamax.de/sportwetten/sports/1/32/36'},
    {'country': 'Spanien', 'league': 'La Liga 2', 'url': 'https://www.winamax.de/sportwetten/sports/1/32/37'},
    {'country': 'Deutschland', 'league': 'Bundesliga', 'url': 'https://www.winamax.de/sportwetten/sports/1/30/42'},
    {'country': 'Deutschland', 'league': '2. Bundesliga', 'url': 'https://www.winamax.de/sportwetten/sports/1/30/41'},
    {'country': 'Deutschland', 'league': '3. Liga', 'url': 'https://www.winamax.de/sportwetten/sports/1/30/8343'},
]

test = parse_winamax('https://www.winamax.de/sportwetten/sports/1/30/8343')
test

df_dict = {(element['country'].replace(" ", "_") + '-' + element['league'].replace(" ", "_")):parse_winamax(url=element['url']) for element in config}
df_dict['Deutschland-3._Liga']

ret = [value.to_csv("data/winamax_" + key + ".csv", index=False) for (key, value) in df_dict.items()]




#### Sportarten, Länder, Ligen

driver = webdriver.Chrome()
driver.get('https://www.winamax.de/sportwetten/')
sports_elements = driver.find_element(By.CSS_SELECTOR, '[class*="sc-iMWBiJ sc-empnci dCNkks dBuJba"]')
sports_elements = driver.find_elements(By.CSS_SELECTOR, '[class*="sc-SrznA fjbnaT"]')

sportarten = sports_elements.text.split("\n")[:-1]
sports_elements[1].find_elements(By.CSS_SELECTOR, '[class*="sc-iMWBiJ sc-empnci PYvJO cDTZGf"]')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import pandas as pd
import time
from datetime import datetime


MARKETS = [
    {'name': 'standard', 'headers': ["1", "X", "2"]}, 
    {'name': 'double-chance', 'headers': ["1X", "12", "X2"]},
    {'name': 'points-more-less-than', 'headers': ["goals_threshold", "+", "-"]},
    {'name': 'score-both', 'headers': ["J", "N"]}
]

driver = webdriver.Chrome()
# driver.implicitly_wait(2)
# driver.get('https://sports.tipico.de/de/alle/fussball/deutschland/bundesliga')




def parse_event(event_element, odds_headers):    
    # odds_headers = ["more_less_goals_than", "+", "-"]
    # event_element = elements[1]
    if event_element.tag_name == 'div':
        return {'date': event_element.text}
    else:
        teams = dict(zip(['home', 'guest'], [team_element.text for team_element in event_element.find_elements(By.CSS_SELECTOR, '[data-gtmid="teamNames"] span')]))

        # fixed_elements = [fixed_element.text for fixed_element in event_element.find_elements(By.CSS_SELECTOR, '[class*="fixed-param-texts"]')]

        odds_group_element = event_element.find_element(By.CSS_SELECTOR, '[data-testid="odd-groups"]')
        
        odds = dict(zip(odds_headers, [
            *[fixed_element.text for fixed_element in event_element.find_elements(By.CSS_SELECTOR, '[class*="fixed-param-texts"]')],
            *[span.text for span in odds_group_element.find_elements(By.TAG_NAME, "span")]
        ]))
        # odds = dict(zip(odds_headers, [span.text for span in odds_group_element.find_elements(By.TAG_NAME, "span")]))
        # odds = dict(zip(odds_headers, event_element.find_element(By.CSS_SELECTOR, 'div:nth-of-type(3)').text.split("\n")))
        return {**teams, **odds}
    

# raw_results = [parse_event(element, odds_headers=["1X", "12", "X2"]) for element in elements]

# # fixed-param-texts
# results = []

# date = raw_results[0]
# for raw_result in raw_results:
#     if len(raw_result) > 1:
#         results.append({**date, **raw_result})
#     else:
#         date = raw_result

# df_results = pd.DataFrame.from_records(results)

# markets = ["standard", "double-chance", "points-more-less-than", "score-both"]
# markets = {
#     'standard': ["1", "X", "2"], 
#     'double-chance': ["1X", "12", "X2"],
#     'points-more-less-than': ["more_less_goals_than", "+", "-"],
#     'score-both': ["J", "N"]
# }



def parse_market(market_config):
    # market_config = markets[0]
    # select_element = driver.find_element(By.CSS_SELECTOR, '[class="SportHeader-styles-module-drop-down"]:nth-of-type(1)')
    select_element = driver.find_element(By.CSS_SELECTOR, '[class="SportHeader-styles-module-drop-down"]')
    select = Select(select_element)
    select.select_by_value(market_config['name'])

    time.sleep(1)

    elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="competition-events"] > *')

    raw_results = [parse_event(element, odds_headers=market_config['headers']) for element in elements]

    results = []

    date = raw_results[0]
    for raw_result in raw_results:
        if len(raw_result) > 1:
            results.append({**date, **raw_result})
        else:
            date = raw_result

    return pd.DataFrame.from_records(results)

# odds_collection = [parse_market(market_config) for market_config in MARKETS]

# len(odds_collection)
# for odds in odds_collection:
#     print(odds)


def parse_tipico(country, league):
    # 1. Navigieren
    # country = 'spanien'
    # league = 'la-liga'
    driver.get('https://sports.tipico.de/de/alle/fussball/' + country + '/' + league)
    
    time.sleep(1)
    try:
        driver.find_element(By.ID, '_evidon-accept-button').click()
    except:
        pass
    
    # 2. Groesse aendern s.d. nur zwei Markets angezeigt sind
    driver.set_window_size(width=1000, height=800)

    # 3. im zweiten Market z.b. head-to-head auswaehlen:
    try:
        select = Select(driver.find_elements(By.CSS_SELECTOR, '[testid="Program_SELECTION"] select')[1])    
        select.select_by_value('head-to-head')
    except:
        pass

    time.sleep(1)
    # 4. market config durchlaufen    
    
    markets_odds = [parse_market(market_config) for market_config in MARKETS]
    markets = [market_odds.set_index(['date', 'home', 'guest']) for market_odds in markets_odds]

    df = pd.concat(markets, axis=1).reset_index(inplace=False)
    df["date"] = df["date"].str.replace(pat=r"\w*, ", repl="", regex=True) \
        .str.replace(pat="Heute", repl=datetime.today().strftime(r"%d.%m")) \
        .apply(lambda value: value + "." + str(datetime.today().year))
    df["date_parsed"] = datetime.now()
    return df


# Tipico:
config = [
    {'country': 'spanien', 'league': 'la-liga'},
    {'country': 'spanien', 'league': 'la-liga-2'},
    {'country': 'deutschland', 'league': 'bundesliga'},
    {'country': 'deutschland', 'league': '2-bundesliga'},
    {'country': 'deutschland', 'league': '3-liga'},
]

# Bet3000:
sport_type = "Fußball"
country = "Deutschland"
league = "Bundesliga"




df_dict = {(element['country'].replace(" ", "_") + '-' + element['league'].replace(" ", "_")):parse_tipico(country=element['country'], league=element['league']) for element in config}


ret = [value.to_csv("data/tipico_" + key + ".csv", index=False) for (key, value) in df_dict.items()]


# import selenium

from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np
import itertools


driver = webdriver.Chrome()
driver.implicitly_wait(2)

def parse_page(base_url, year, matchday):

    driver.get(base_url + str(year) + "/" + str(matchday))

    # Close cookies alert:
    try: 
        driver.find_element(by=By.CSS_SELECTOR, value="[aria-label='Einwilligen']").click()
    except:
        pass

    # matches = driver.find_elements(by=By.CSS_SELECTOR, value="[class='spiele-row detils']")

    data = [{
        'match_details': result.get_attribute('title'),
        'score': [score.text for score in result.find_elements(by=By.TAG_NAME, value="span")]
    } for result in driver.find_elements(by=By.CSS_SELECTOR, value="[class='ergebnis']")]

    data = [{
        'description': match['match_details'],
        'full_time': match['score'][0],
        'half_time': match['score'][1]
    } for match in data]


    df_bundesliga = pd.DataFrame.from_records(data)
    df_bundesliga[["home", "guest", "date", "league"]] = df_bundesliga["description"].str.extract(pat=r'Spieldetails: (.+) gegen (.+) \((.+), (.+)\)', expand=False)
    df_bundesliga["season"] = year
    df_bundesliga["matchday"] = matchday
    df_bundesliga.drop(columns="description", inplace=True)
    return(df_bundesliga)


#"https://www.fussballdaten.de/bundesliga/2024/15/"
# base_url = ["https://www.fussballdaten.de/bundesliga/", "https://www.fussballdaten.de/2liga/"]
base_url = ["https://www.fussballdaten.de/2liga/"]
years = [2024]
# matchdays = range(1, 18)
matchdays = [18]

config = [dict(zip(['base_url', 'year', 'matchday'], values)) for values in itertools.product(base_url, years, matchdays)]

data_collection = [parse_page(**page) for page in config]

pd.concat(data_collection).reset_index(drop=True).to_excel("2_liga_daten_2024_18.xlsx")


def compute_streaks(path):
    df_results = pd.read_excel(path, index_col=0)

    df_results[["goals_home", "goals_guest"]] = df_results["full_time"].str.extract(r"(\d):(\d)")
    df_results["winner"] = np.where((df_results["goals_home"] > df_results["goals_guest"]), "home",
                            np.where((df_results["goals_guest"] > df_results["goals_home"]), "guest", "x"))
                                    


    df_results = df_results.melt(id_vars=["matchday", "winner"], value_vars=["home", "guest"], value_name="team", var_name="home_or_guest")
    df_results["win"] = df_results["winner"] == df_results["home_or_guest"]
    df_results["lose"] = (df_results["winner"] != df_results["home_or_guest"]) & (df_results["winner"] != "x")
    df_results = df_results.sort_values(["team", "matchday"], ascending=[True, False])

    df_streaks = pd.concat([df_results.groupby("team")["lose"].apply(lambda group: group.tolist()), df_results.groupby("team")["win"].apply(lambda group: group.tolist())], axis=1)

    def find_first_match(input, value):
        try:
            return(input.index(value))
        except:
            return len(input)


    df_streaks["win_streak"] = df_streaks["win"].apply(find_first_match, value=False)
    df_streaks["lose_streak"] = df_streaks["lose"].apply(find_first_match, value=False)
    df_streaks["non_win_streak"] = df_streaks["win"].apply(find_first_match, value=True)
    df_streaks["non_lose_streak"] = df_streaks["lose"].apply(find_first_match, value=True)
    
    return df_streaks.reset_index().drop(columns=["win", "lose"])



compute_streaks("2_liga_daten_2024.xlsx")



driver = webdriver.Chrome()

driver.get('https://bet3000.de/sports')

driver.find_element(By.ID, value="onetrust-accept-btn-handler").click()

driver.get('https://www.winamax.de/sportwetten/sports/1/30/42')
driver.find_element(By.ID, value="tarteaucitronAllDenied2").click()
driver.find_element(By.TAG_NAME, "button").click()
driver.find_element(By.CSS_SELECTOR)

driver.get('https://www.tipwin.de/de/sports/full')
element = driver.find_element(By.NAME, value="Deutschland")
element.find_element(By.XPATH, value="./../..").click()

driver.find_element(By.NAME, "Bundesliga").find_element(By.XPATH, value="./..").click()


driver.get('https://sports.tipico.de/de/alle/fussball/deutschland/bundesliga')
driver.find_element(By.ID, '_evidon-accept-button').click()





home = [1,4,7]
tie = [2,5,8]
guest = [3,6,9]

import itertools
combinations = itertools.product(home, tie, guest)
[print(combination) for combination in combinations]
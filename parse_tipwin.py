from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import pandas as pd
import time
from datetime import datetime

driver = webdriver.Chrome()

driver.set_window_size(width=1920, height=1080)

driver.get('https://www.tipwin.de/de/sports/full')

# close popup:
try:
    driver.find_element(By.CSS_SELECTOR, '[class*="popup__card"] button').click()
except:
    pass


# Open Deutschland dropdown:
driver.find_element(By.NAME, value="Deutschland").find_element(By.XPATH, value="./../..").click()

# Check Bundesliga:
driver.find_element(By.NAME, "Bundesliga").find_element(By.XPATH, value="./..").click()

# change last select:
driver.find_element(By.CSS_SELECTOR, '[class*="offer__type__select"]:nth-of-type(4)')
select = Select(driver.find_elements(By.TAG_NAME, "select")[3])
select.select_by_value("will-both-teams-score")

row_elements = driver.find_elements(By.CSS_SELECTOR, '[class*="offer__body__row"]')



# headers = ["day", "time", "home", "guest", "1", "X", "2", "1X", "12", "X2", "goals_threshold", "+", "-", "J", "N"]
HEADERS = ["date", "time", "home", "guest", "1", "X", "2", "1X", "12", "X2", "goals_threshold", "+", "-", "J", "N"]

def parse_row(row_element):
    data = row_element.text.split("\n")[:-1]
    try:
        data.pop(data.index('LIVE'))
    except:
        pass
    return dict(zip(HEADERS, data))


df = pd.DataFrame.from_records([parse_row(row_element) for row_element in row_elements])


def parse_tipwin(country, league):
    driver.set_window_size(width=3000, height=1080)
    driver.get('https://www.tipwin.de/de/sports/full')

    # close popup:
    try:
        driver.find_element(By.CSS_SELECTOR, '[class*="popup__card"] button').click()
    except:
        pass


    time.sleep(3)

    # Open country dropdown:
    driver.find_element(By.NAME, value=country).find_element(By.XPATH, value="./../..").click()
    time.sleep(1)

    # Check league:
    driver.find_element(By.NAME, league).find_element(By.XPATH, value="./..").click()
    time.sleep(1)

    # change last select:    
    select = Select(driver.find_elements(By.TAG_NAME, "select")[3])
    select.select_by_value("will-both-teams-score")

    row_elements = driver.find_elements(By.CSS_SELECTOR, '[class*="offer__body__row"]')

    df = pd.DataFrame.from_records([parse_row(row_element) for row_element in row_elements])
    df["date"] = df["date"].str.replace(pat=r"\w{2} ", repl="", regex=True).str.replace(pat="Heute", repl=datetime.today().strftime(r"%d.%m.")) \
        .str.replace(pat="Mrg", repl=datetime(year=datetime.today().year, month=datetime.today().month, day=datetime.today().day + 1).strftime(r"%d.%m.")) \
        .apply(lambda value: value + str(datetime.today().year))
    df["date_parsed"] = datetime.now()
    return df



config = [
    {'country': 'Spanien', 'league': 'La Liga'},
    {'country': 'Spanien', 'league': 'La Liga 2'},
    {'country': 'Deutschland', 'league': 'Bundesliga'},
    {'country': 'Deutschland', 'league': '2. Bundesliga'},
    {'country': 'Deutschland', 'league': '3. Liga'},
]
# dfs = [parse_tipwin(country=element['country'], league=element['league']) for element in config]
df_dict = {(element['country'].replace(" ", "_") + '-' + element['league'].replace(" ", "_")):parse_tipwin(country=element['country'], league=element['league']) for element in config}

ret = [value.to_csv("data/tipwin_" + key + ".csv", index=False) for (key, value) in df_dict.items()]




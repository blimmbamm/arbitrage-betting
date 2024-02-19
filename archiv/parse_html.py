from bs4 import BeautifulSoup

file = open("bet365 - Sportwetten Online.html", 'r', encoding='utf-8')
html_content = file.read()

soup = BeautifulSoup(html_content, 'lxml')
team_names = soup.find_all(attrs={'class': 'rcl-ParticipantFixtureDetailsTeam_TeamNames'})
team_names = soup.find_all(attrs={'class': 'rcl-ParticipantFixtureDetailsTeam_TeamName'})
len(team_names)
team_names[0]

odds = soup.find_all(attrs={'class': 'sgl-ParticipantOddsOnly80_Odds'})

len(odds)
odds[:21]
type(soup)
team_names[0].find_all(attrs={'class': 'sgl-ParticipantOddsOnly80_Odds'})

odds_columns = soup.find_all("div", class_='sgl-MarketOddsExpand')
market = [element.find(class_="rcl-MarketColumnHeader").text for element in odds_columns]

odds = [[element.text for element in odds_column.find_all("span", class_='sgl-ParticipantOddsOnly80_Odds')] for odds_column in odds_columns]


# odds_home = [element.text for element in odds_columns[0].find_all("span", class_='sgl-ParticipantOddsOnly80_Odds')]
# odds_x = [element.text for element in odds_columns[1].find_all("span", class_='sgl-ParticipantOddsOnly80_Odds')]
# odds_guest = [element.text for element in odds_columns[2].find_all("span", class_='sgl-ParticipantOddsOnly80_Odds')]

1/float(odds[0][0])
[dict(dingens=market_odds) for market_odds in odds]
dict()
import pandas as pd
import numpy as np
df_odds = pd.DataFrame.from_records(odds).transpose()
df_odds = df_odds.astype('float')
df_odds.apply(np.reciprocal).apply(sum, axis=1)
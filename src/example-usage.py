import sys
sys.path.append("src")

from tipico_parser import TipicoParser
# from bet3000_parser import Bet3000Parser
# from tipwin_parser import TipwinParser
# from winamax_parser import WinamaxParser
from config import Config
from odds_analyzer import OddsAnalyzer


# Seed configs database:
Config.insert_configs(Config.from_csv('config_setup.csv'))

# Create new config from scratch:
config = Config(bookmaker='tipico', sports='icehockey', country='usa', league='NHL', config={'url': 'https://sports.tipico.de/de/alle/eishockey/usa/nhl'})
# Persist in databse:
config.insert_config()


# Retrieve all configs:
configs = Config.get_configs(query={})

# Retrieve some configs, e.g. all for tipico:
configs = Config.get_configs(query={'bookmaker': 'tipico'})

# Initialize parser:
parser = TipicoParser()

# Parse:
results = parser.parse(configs=configs)

# Inspect:
print(results)

# Push to database:
parser.push_to_database(results)

# ... and basically repeat for other bookmakers ...


# In order to compare odds from different bookmakers, all (potentially differing) team names must be unified. 
# Hence, there is the possibility to only parse team names:
teams = parser.parse_teams(configs=configs)

# New team names are then pushed to a Google sheet, where one manually adds the mapping in cases where needed:
parser.push_teams_to_google_sheets(teams)

# Once updated in Google sheets, the new teams mapping is pulled from Google sheets and stored as csv:
parser.update_teams_mapping()


# Now, analyze odds and view results to see if there is an arbitrage opportunity:
analyzer = OddsAnalyzer()
d = analyzer.analyze()
print(d.head())



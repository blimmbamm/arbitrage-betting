import sys
sys.path.append("src")

# from bet3000_parser import Bet3000Parser
# from tipico_parser import TipicoParser
# from tipwin_parser import TipwinParser
from config import Config
from winamax_parser import WinamaxParser


config_dict = {
    'bookmaker': 'bet3000',
    'sports': 'fussball', 
    'country': 'spanien', 
    'league': 'la-liga', 
    'config': {
        'sports': 'Fußball', 
        'country': 'Spanien', 
        'league': 'La Liga'
    }
}
config_dict = {'bookmaker': 'tipico', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga'}}
config_dict = {'bookmaker': 'tipwin', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'sports': 'Fussball', 'country': 'Spanien', 'league': 'La Liga'}}
config_dict_2 = {'bookmaker': 'tipwin', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'sports': 'Fussball', 'country': 'Deutschland', 'league': 'Bundesliga'}}
config_dict_3 = {'bookmaker': 'winamax', 'sports': 'fussball', 'country': 'italien', 'league': 'serie-a', 
                 'config': {
                     'url': 'https://www.winamax.de/sportwetten/sports/1/31/33'
                 }}
config_dict_4 = {'bookmaker': 'winamax', 'sports': 'fussball', 'country': 'italien', 'league': 'serie-a', 
                 'config': {
                     'url': 'https://www.winamax.de/sportwetten/sports/1/30/8343'
                 }}


test_config = Config(**config_dict_3)
test_config_2 = Config(**config_dict_4)
# parser = Bet3000Parser()
# parser = TipicoParser()
# parser = TipwinParser()
parser = WinamaxParser()

# print(parser.parse_single(config=test_config))
# print(parser.parse_teams(configs=[test_config, test_config]))
# parser.parse_single(test_config)
results = parser.parse(configs=[test_config, test_config_2])
results = parser.parse_teams(configs=[test_config])



CONFIG = [
    {'bookmaker': 'tipico', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga'}},
    {'bookmaker': 'tipwin', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'sports': 'Fussball', 'country': 'Spanien', 'league': 'La Liga'}},
    {'bookmaker': 'winamax', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'url': 'https://www.winamax.de/sportwetten/sports/1/32/36'}},
    {'bookmaker': 'bet3000', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'sports': 'Fußball', 'country': 'Spanien', 'league': 'La Liga'}},
    {'bookmaker': 'bet3000', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga-2', 'config': {'sports': 'Fußball', 'country': 'Spanien', 'league': 'La Liga 2'}},
    {'bookmaker': 'bet3000', 'sports': 'eishockey', 'country': 'schweden', 'league': 'shl', 'config': {'sports': 'Eishockey', 'country': 'Schweden', 'league': 'SHL'}}
]

market = {
    'bookmaker': 'bet3000',
    'sports': 'fussball',
    'markets': [
        {
            'market_description': 'Standard',
            'market': '0: Object',
            'relevant_indices': [0, 2, 3, 5, 7, 9],
            'headers': ["date", "home", "guest", "1", "X", "2"]
        },
        {
            'market_description': 'Doppelte Chance',
            'market': '3: Object',
            'relevant_indices': [0, 2, 3, 5, 7, 9],
            'headers': ["date", "home", "guest", "1X", "12", "X2"]
        },
        {
            'market_description': 'Beide Teams treffen',
            'market': '4: Object',
            'relevant_indices': [0, 2, 3, 5, 7],
            'headers': ["date", "home", "guest", "J", "N"]
        }
    ]
}
MARKETS = {
    'fussball': [
        {
            'market_description': 'Standard',
            'market': '0: Object',
            'relevant_indices': [0, 2, 3, 5, 7, 9],
            'headers': ["date", "home", "guest", "1", "X", "2"]
        },
        {
            'market_description': 'Doppelte Chance',
            'market': '3: Object',
            'relevant_indices': [0, 2, 3, 5, 7, 9],
            'headers': ["date", "home", "guest", "1X", "12", "X2"]
        },
        {
            'market_description': 'Beide Teams treffen',
            'market': '4: Object',
            'relevant_indices': [0, 2, 3, 5, 7],
            'headers': ["date", "home", "guest", "J", "N"]
        }
    ], 
    'eishockey': [
        {
            'market_description': 'Standard',
            'market': '0: Object',
            'relevant_indices': [0, 2, 3, 5, 7, 9],
            'headers': ["date", "home", "guest", "1", "X", "2"]
        },
        {
            'market_description': 'Doppelte Chance',
            'market': '3: Object',
            'relevant_indices': [0, 2, 3, 5, 7, 9],
            'headers': ["date", "home", "guest", "1X", "12", "X2"]
        },
        {
            'market_description': 'Beide Teams treffen',
            'market': '4: Object',
            'relevant_indices': [0, 2, 3, 5, 7],
            'headers': ["date", "home", "guest", "J", "N"]
        }
    ],
    'handball': []
}

parser = Bet3000Parser()
results = parser.parse(CONFIG[3])
parser.refresh()
results = parser.parse_multiple(CONFIG[3:])
[dict(result) for result in results[0]]

parser.parse_teams(CONFIG[5:])

parser.parse(CONFIG[5])

parser.get_elements_text()
from datetime import date
date.today()









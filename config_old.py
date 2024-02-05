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

# Tipwin:
config = [
    {'country': 'Spanien', 'league': 'La Liga'},
    {'country': 'Spanien', 'league': 'La Liga 2'},
    {'country': 'Deutschland', 'league': 'Bundesliga'},
    {'country': 'Deutschland', 'league': '2. Bundesliga'},
    {'country': 'Deutschland', 'league': '3. Liga'},
]

# Winamax:
config = [
    {'country': 'Spanien', 'league': 'La Liga', 'url': 'https://www.winamax.de/sportwetten/sports/1/32/36'},
    {'country': 'Spanien', 'league': 'La Liga 2', 'url': 'https://www.winamax.de/sportwetten/sports/1/32/37'},
    {'country': 'Deutschland', 'league': 'Bundesliga', 'url': 'https://www.winamax.de/sportwetten/sports/1/30/42'},
    {'country': 'Deutschland', 'league': '2. Bundesliga', 'url': 'https://www.winamax.de/sportwetten/sports/1/30/41'},
    {'country': 'Deutschland', 'league': '3. Liga', 'url': 'https://www.winamax.de/sportwetten/sports/1/30/8343'},
]

CONFIG = [
    {'bookmaker': 'tipico', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga'}},
    {'bookmaker': 'tipwin', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'sports': 'Fussball', 'country': 'Spanien', 'league': 'La Liga'}},
    {'bookmaker': 'winamax', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'url': 'https://www.winamax.de/sportwetten/sports/1/32/36'}},
    {'bookmaker': 'bet3000', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'sports': 'Fussball', 'country': 'Spanien', 'league': 'La Liga'}},
]

CONFIG[2].get('config')

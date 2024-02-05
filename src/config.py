class Config:
    
    bookmaker: str
    sports: str
    country: str
    league: str
    config: dict

    def __init__(self, bookmaker, sports, country, league, config) -> None:
        self.bookmaker = bookmaker
        self.sports = sports
        self.country = country
        self.league = league
        self.config = config


    @classmethod
    def from_dict(cls, dict):
        return cls(**dict)

    
my_config = Config(**{'bookmaker': 'tipico', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga'}})
my_config_2 = Config.from_dict({'bookmaker': 'tipico', 'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga', 'config': {'sports': 'fussball', 'country': 'spanien', 'league': 'la-liga'}})
my_config_2.config
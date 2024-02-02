import pandas as pd
from unidecode import unidecode 
from datetime import datetime
import numpy as np

ODDS_HEADERS = ['1', 'X', '2', '1X', '12', 'X2', 'goals_threshold', '+', '-', 'J', 'N']

def create_team_mapping(file_all_team_names, file_out):
    df_teams = pd.read_excel(file_all_team_names)
    df_teams.drop_duplicates(subset=['country', 'league', 'id']).to_csv(file_out, index=False)
    

def normalize_data(df: pd.DataFrame):
    # Unidecode special characters:    
    df["home"] = df["home"].apply(unidecode)
    df["guest"] = df["guest"].apply(unidecode)
    
    # Convert date string to date
    df["date"] = df["date"].apply(lambda value: datetime.strptime(value, "%d.%m.%Y"))
    
    # Join team id:
    df_teams = pd.read_csv("teams.csv").set_index(['country', 'league', 'team'])
    df = df.join(df_teams.rename(columns={'id': 'id_home'}), on=['country', 'league', 'home'])
    df = df.join(df_teams.rename(columns={'id': 'id_guest'}), on=['country', 'league', 'guest'])
    df.drop(columns=['home', 'guest'], inplace=True)
    
    # Join names from team names mapping table
    df_team_names = pd.read_csv("teams_mapping.csv").set_index(['country', 'league', 'id'])    
    df = df.join(df_team_names.rename(columns={'team': 'home'}), on=['country', 'league', 'id_home'])
    df = df.join(df_team_names.rename(columns={'team': 'guest'}), on=['country', 'league', 'id_guest'])
        
    # Replace empty string "" by nan:
    df.replace("", np.nan, inplace=True)
    
    # Convert odds to numerics:    
    df[df.columns.intersection(ODDS_HEADERS)] = df[df.columns.intersection(ODDS_HEADERS)] \
        .apply(lambda col: col.astype('string')) \
        .apply(lambda col: col.str.replace(",", ".").astype('float'))
    
    # Replace NA quotes by 1:
    df.fillna(value=1, inplace=True)
    
    # Add date parsed:
    df["date_parsed"] = datetime.now()
    return df



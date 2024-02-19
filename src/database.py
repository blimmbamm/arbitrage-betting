import gspread
import pymongo

gc = gspread.service_account("secrets/sports-teams-413107-030845340458.json")
teams = gc.open('teams').sheet1

client = pymongo.MongoClient(open('secrets/mongodb').read())

odds_collection = client.get_database('arbitrage-betting').get_collection('odds')

configs_collection = client.get_database('arbitrage-betting').get_collection('configs')
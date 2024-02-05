import gspread

gc = gspread.service_account("secrets/sports-teams-413107-030845340458.json")

teams = gc.open('teams')
teams.sheet1.get_all_records()
teams.sheet1.cell(5, 1).value = "hallo"
teams.sheet1.update_cell(1, 5, "hallo")

from nba_api.stats.endpoints import commonplayerinfo
import time

# Test plusieurs joueurs de différents postes
test_players = {
    'Stephen Curry (PG)': 201939,
    'LeBron James (SF)': 2544,
    'Giannis (PF)': 203507,
    'Nikola Jokic (C)': 203999,
    'Luka Doncic (PG)': 1629029,
}

print("Test API commonplayerinfo - Positions retournées:\n")
for name, player_id in test_players.items():
    try:
        info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
        df = info.get_data_frames()[0]
        position = df['POSITION'].values[0]
        print(f"{name:25s} → '{position}'")
        time.sleep(0.6)
    except Exception as e:
        print(f"{name:25s} → ERREUR: {e}")

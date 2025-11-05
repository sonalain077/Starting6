"""
Test du 3 novembre 2025 pour voir s'il y a des matchs avec des stats
"""
from datetime import datetime
from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2
import time

game_date = "2025-11-03"

print(f"📅 Test de la date : {game_date}")
print(f"🔍 Récupération des matchs...\n")

try:
    # Récupérer les matchs
    scoreboard = scoreboardv2.ScoreboardV2(game_date=game_date)
    games = scoreboard.get_data_frames()[0]
    
    print(f"✅ {len(games)} match(s) trouvé(s)")
    
    if not games.empty:
        # Prendre le premier match
        first_game = games.iloc[0]
        game_id = first_game['GAME_ID']
        
        print(f"\n🎯 Test du match : {game_id}")
        
        time.sleep(0.5)
        
        # Récupérer les stats
        boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
        player_stats = boxscore.get_data_frames()[0]
        
        print(f"📊 Stats joueurs : {len(player_stats)} joueurs")
        
        if len(player_stats) > 0:
            print(f"\n✅ SUCCÈS ! Données trouvées pour {game_date}")
            print(f"\n   Top 5 scoreurs :")
            
            # Trier par points
            top_scorers = player_stats.nlargest(5, 'PTS')
            for i, p in enumerate(top_scorers.iterrows(), 1):
                player = p[1]
                print(f"      {i}. {player['PLAYER_NAME']:25} : {player['PTS']:2.0f} PTS, {player['REB']:2.0f} REB, {player['AST']:2.0f} AST")
        else:
            print(f"\n⚠️  Aucune stat disponible pour {game_date}")
            print("   Les matchs n'ont peut-être pas encore eu lieu ou les stats ne sont pas disponibles")
    else:
        print(f"\n⚠️  Aucun match trouvé pour {game_date}")

except Exception as e:
    print(f"\n❌ Erreur : {e}")
    import traceback
    traceback.print_exc()

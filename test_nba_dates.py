"""
Test avec différentes dates pour trouver des matchs avec des stats
"""
from datetime import datetime, timedelta
from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2
import time

# Essayer plusieurs dates
dates_to_try = [
    datetime(2024, 11, 4),  # Il y a exactement 1 an
    datetime(2024, 3, 15),  # Mi-saison 2023-24
    datetime(2024, 2, 1),   # Début 2024
]

for test_date in dates_to_try:
    game_date = test_date.strftime("%Y-%m-%d")
    
    print(f"\n{'='*70}")
    print(f"📅 Test de la date : {game_date}")
    print(f"{'='*70}")
    
    try:
        # Récupérer les matchs
        scoreboard = scoreboardv2.ScoreboardV2(game_date=game_date)
        games = scoreboard.get_data_frames()[0]
        
        print(f"✅ {len(games)} match(s) trouvé(s)")
        
        if not games.empty:
            # Prendre le premier match
            first_game = games.iloc[0]
            game_id = first_game['GAME_ID']
            
            print(f"\n🎯 Match : {game_id}")
            
            time.sleep(0.5)
            
            # Récupérer les stats
            boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
            player_stats = boxscore.get_data_frames()[0]
            
            print(f"📊 Stats joueurs : {len(player_stats)} joueurs")
            
            if len(player_stats) > 0:
                print(f"\n✅ SUCCÈS ! Données trouvées pour {game_date}")
                print(f"\n   Top 3 joueurs :")
                for i in range(min(3, len(player_stats))):
                    p = player_stats.iloc[i]
                    print(f"      {i+1}. {p['PLAYER_NAME']} : {p['PTS']} PTS, {p['REB']} REB, {p['AST']} AST")
                
                # Arrêter après avoir trouvé des données
                break
        else:
            print("   ⚠️  Aucun match ce jour-là")
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
        continue
    
    time.sleep(1)  # Rate limiting

print(f"\n{'='*70}")
print("✅ Test terminé")

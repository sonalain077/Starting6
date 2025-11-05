"""
Test direct de l'API NBA pour voir ce qui est retourné
"""
from datetime import datetime, timedelta
from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2
import time

# Date d'hier
yesterday = datetime.now() - timedelta(days=1)
game_date = yesterday.strftime("%Y-%m-%d")

print(f"📅 Date testée : {game_date}")
print(f"🔍 Récupération des matchs...\n")

try:
    # Récupérer la liste des matchs
    scoreboard = scoreboardv2.ScoreboardV2(game_date=game_date)
    games = scoreboard.get_data_frames()[0]
    
    print(f"✅ {len(games)} match(s) trouvé(s)")
    
    if games.empty:
        print("\n⚠️  Aucun match trouvé pour cette date")
        print("   Les matchs NBA ont peut-être lieu à d'autres dates")
        print("   Essayons une autre date...")
        
        # Essayer il y a 2 jours
        yesterday = datetime.now() - timedelta(days=2)
        game_date = yesterday.strftime("%Y-%m-%d")
        print(f"\n📅 Nouvelle date : {game_date}")
        
        scoreboard = scoreboardv2.ScoreboardV2(game_date=game_date)
        games = scoreboard.get_data_frames()[0]
        print(f"✅ {len(games)} match(s) trouvé(s)")
    
    if not games.empty:
        # Prendre le premier match
        first_game = games.iloc[0]
        game_id = first_game['GAME_ID']
        
        print(f"\n🎯 Test du match : {game_id}")
        print(f"   {first_game.get('HOME_TEAM_ID', 'N/A')} vs {first_game.get('VISITOR_TEAM_ID', 'N/A')}")
        
        time.sleep(0.5)
        
        # Récupérer les stats du match
        print(f"\n🔄 Récupération du boxscore...")
        boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
        
        # Voir tous les DataFrames disponibles
        all_dfs = boxscore.get_data_frames()
        print(f"\n📊 Nombre de DataFrames retournés : {len(all_dfs)}")
        
        for i, df in enumerate(all_dfs):
            print(f"\n   DataFrame {i} : {len(df)} lignes, {len(df.columns)} colonnes")
            if not df.empty:
                print(f"   Colonnes : {list(df.columns)[:10]}")
                print(f"\n   Aperçu des premières lignes :")
                print(df.head(3))
        
        # Test avec le premier DataFrame (normalement les stats des joueurs)
        if len(all_dfs) > 0:
            player_stats = all_dfs[0]
            print(f"\n✅ Stats joueurs : {len(player_stats)} joueurs")
            
            if len(player_stats) > 0:
                print(f"\n   Premier joueur :")
                first_player = player_stats.iloc[0]
                print(f"      Nom : {first_player.get('PLAYER_NAME', 'N/A')}")
                print(f"      ID : {first_player.get('PLAYER_ID', 'N/A')}")
                print(f"      PTS : {first_player.get('PTS', 'N/A')}")
                print(f"      REB : {first_player.get('REB', 'N/A')}")
                print(f"      AST : {first_player.get('AST', 'N/A')}")

except Exception as e:
    print(f"\n❌ Erreur : {e}")
    import traceback
    traceback.print_exc()

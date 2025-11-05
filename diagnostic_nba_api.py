"""
Diagnostic complet pour comprendre pourquoi les données ne sont pas disponibles
"""
from datetime import datetime, timedelta
from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2
from nba_api.stats.static import teams
import time

print("🔍 DIAGNOSTIC COMPLET DE L'API NBA")
print("="*80)

# 1. Vérifier les équipes disponibles
print("\n1️⃣ Vérification des équipes NBA...")
nba_teams = teams.get_teams()
print(f"   ✅ {len(nba_teams)} équipes trouvées")
print(f"   Exemple: {nba_teams[0]['full_name']}")

# 2. Tester plusieurs dates récentes
print("\n2️⃣ Test de plusieurs dates récentes...")
dates_to_test = [
    (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") 
    for i in range(7)  # Les 7 derniers jours
]

for game_date in dates_to_test:
    try:
        scoreboard = scoreboardv2.ScoreboardV2(game_date=game_date)
        games = scoreboard.get_data_frames()[0]
        
        if not games.empty:
            # Tester le premier match
            game_id = games.iloc[0]['GAME_ID']
            
            time.sleep(0.5)
            boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
            player_stats = boxscore.get_data_frames()[0]
            
            status = "✅ DONNÉES OK" if len(player_stats) > 0 else "⚠️ VIDE"
            print(f"   {game_date}: {len(games):2} matchs, {len(player_stats):2} joueurs - {status}")
            
            if len(player_stats) > 0:
                print(f"      🎯 Premier match avec données: {game_id}")
                top_scorer = player_stats.nlargest(1, 'PTS').iloc[0]
                print(f"      ⭐ Top scorer: {top_scorer['PLAYER_NAME']} - {top_scorer['PTS']:.0f} PTS")
                break  # On arrête après avoir trouvé des données
        else:
            print(f"   {game_date}: Aucun match")
            
    except Exception as e:
        print(f"   {game_date}: Erreur - {e}")
    
    time.sleep(0.3)

# 3. Vérifier les détails d'un match récent
print("\n3️⃣ Analyse détaillée d'un match récent...")
try:
    recent_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"   Date: {recent_date}")
    
    scoreboard = scoreboardv2.ScoreboardV2(game_date=recent_date)
    games_df = scoreboard.get_data_frames()[0]
    
    if not games_df.empty:
        print(f"   Colonnes disponibles dans le scoreboard:")
        print(f"   {list(games_df.columns)[:10]}")
        
        first_game = games_df.iloc[0]
        print(f"\n   Premier match:")
        print(f"      Game ID: {first_game.get('GAME_ID', 'N/A')}")
        print(f"      Status: {first_game.get('GAME_STATUS_TEXT', 'N/A')}")
        print(f"      Home: {first_game.get('HOME_TEAM_ID', 'N/A')}")
        print(f"      Visitor: {first_game.get('VISITOR_TEAM_ID', 'N/A')}")
        
        # Essayer de récupérer les stats
        game_id = first_game['GAME_ID']
        time.sleep(0.5)
        
        print(f"\n   Tentative de récupération du boxscore {game_id}...")
        boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
        all_dfs = boxscore.get_data_frames()
        
        print(f"   📊 {len(all_dfs)} DataFrames retournés:")
        for i, df in enumerate(all_dfs):
            print(f"      DF {i}: {len(df)} lignes, {len(df.columns) if not df.empty else 0} colonnes")
            if not df.empty and len(df.columns) > 0:
                print(f"         Colonnes: {list(df.columns)[:8]}")
        
        # Vérifier si c'est un problème de timing
        if all(len(df) == 0 for df in all_dfs):
            print(f"\n   ⚠️  DIAGNOSTIC:")
            print(f"      - Le match existe dans le scoreboard")
            print(f"      - Mais le boxscore est vide")
            print(f"      - Status du match: {first_game.get('GAME_STATUS_TEXT', 'N/A')}")
            print(f"\n   💡 CAUSES POSSIBLES:")
            print(f"      1. Match pas encore joué (futur)")
            print(f"      2. Match en cours (live)")
            print(f"      3. Stats pas encore disponibles (délai API)")
            print(f"      4. Saison pas encore commencée officiellement")
    else:
        print(f"   ⚠️  Aucun match trouvé pour {recent_date}")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# 4. Vérifier la saison en cours
print("\n4️⃣ Vérification de la saison NBA...")
print(f"   Date actuelle: {datetime.now().strftime('%Y-%m-%d')}")
print(f"   Saison NBA 2025-2026:")
print(f"      - Début habituel: Octobre 2025")
print(f"      - Nous sommes: Novembre 2025")
print(f"\n   💡 NOTE: La saison 2025-26 vient probablement juste de commencer")
print(f"      L'API peut avoir un délai de quelques heures pour publier les stats")

print("\n" + "="*80)
print("✅ Diagnostic terminé")
print("\n📝 RECOMMANDATION:")
print("   - Utiliser des données de test de 2024 pour valider le système")
print("   - Ou attendre quelques heures/jours pour les données live 2025")
print("   - Vérifier le site officiel NBA.com pour voir si les stats sont publiées")

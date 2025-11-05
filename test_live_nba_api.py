"""
Test de l'API live.nba pour accéder aux données en temps réel
"""
from nba_api.live.nba.endpoints import scoreboard, boxscore
from datetime import datetime, timedelta
import json

print("🔴 TEST DE L'API LIVE NBA")
print("=" * 80)

# Test 1: Scoreboard d'aujourd'hui
print("\n1️⃣ Récupération du scoreboard live...")
try:
    board = scoreboard.ScoreBoard()
    data = board.get_dict()
    
    games = data.get('scoreboard', {}).get('games', [])
    print(f"   ✅ {len(games)} match(s) trouvé(s) aujourd'hui")
    
    if games:
        print("\n   📋 Liste des matchs:")
        for i, game in enumerate(games[:5], 1):  # Afficher max 5 matchs
            game_id = game.get('gameId', 'N/A')
            home_team = game.get('homeTeam', {}).get('teamTricode', 'N/A')
            away_team = game.get('awayTeam', {}).get('teamTricode', 'N/A')
            game_status = game.get('gameStatusText', 'N/A')
            
            print(f"      {i}. {away_team} @ {home_team}")
            print(f"         Game ID: {game_id}")
            print(f"         Status: {game_status}")
            
except Exception as e:
    print(f"   ❌ Erreur: {e}")

# Test 2: Boxscore d'un match spécifique (celui de votre screenshot)
print("\n2️⃣ Test du boxscore du match MIL vs TOR (0022500165)...")
try:
    # Ce Game ID vient de votre screenshot
    game_id = "0022500165"
    box = boxscore.BoxScore(game_id=game_id)
    data = box.get_dict()
    
    # Structure de l'API live
    game_data = data.get('game', {})
    home_team = game_data.get('homeTeam', {})
    away_team = game_data.get('awayTeam', {})
    
    print(f"   🏀 Match: {away_team.get('teamTricode')} @ {home_team.get('teamTricode')}")
    print(f"   📅 Status: {game_data.get('gameStatusText', 'N/A')}")
    
    # Récupérer les joueurs
    home_players = home_team.get('players', [])
    away_players = away_team.get('players', [])
    all_players = home_players + away_players
    
    print(f"\n   📊 Stats joueurs: {len(all_players)} joueurs")
    
    if all_players:
        print("\n   🌟 Top 5 joueurs par points:")
        # Trier par points
        sorted_players = sorted(
            all_players,
            key=lambda p: p.get('statistics', {}).get('points', 0),
            reverse=True
        )
        
        for i, player in enumerate(sorted_players[:5], 1):
            name = player.get('name', 'Unknown')
            stats = player.get('statistics', {})
            pts = stats.get('points', 0)
            reb = stats.get('reboundsTotal', 0)
            ast = stats.get('assists', 0)
            
            print(f"      {i}. {name}: {pts} PTS, {reb} REB, {ast} AST")
        
        print(f"\n   ✅ SUCCÈS ! L'API live.nba fonctionne pour ce match")
        
        # Afficher la structure complète du premier joueur
        print("\n   📋 Structure des données joueur (exemple):")
        first_player = all_players[0]
        print(f"      Nom: {first_player.get('name')}")
        print(f"      Position: {first_player.get('position')}")
        print(f"      Statistics disponibles:")
        stats = first_player.get('statistics', {})
        for key in ['points', 'reboundsTotal', 'assists', 'steals', 'blocks', 
                    'turnovers', 'fieldGoalsMade', 'fieldGoalsAttempted',
                    'threePointersMade', 'threePointersAttempted',
                    'freeThrowsMade', 'freeThrowsAttempted', 'foulsPersonal']:
            if key in stats:
                print(f"         - {key}: {stats.get(key)}")
    else:
        print("   ⚠️  Aucun joueur trouvé (match pas encore joué?)")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Essayer avec tous les matchs récents
print("\n3️⃣ Recherche de matchs avec données disponibles...")
try:
    board = scoreboard.ScoreBoard()
    data = board.get_dict()
    games = data.get('scoreboard', {}).get('games', [])
    
    games_with_data = 0
    for game in games:
        game_id = game.get('gameId')
        try:
            box = boxscore.BoxScore(game_id=game_id)
            box_data = box.get_dict()
            
            home_players = box_data.get('game', {}).get('homeTeam', {}).get('players', [])
            away_players = box_data.get('game', {}).get('awayTeam', {}).get('players', [])
            
            if home_players or away_players:
                games_with_data += 1
                home_team = game.get('homeTeam', {}).get('teamTricode', 'N/A')
                away_team = game.get('awayTeam', {}).get('teamTricode', 'N/A')
                print(f"   ✅ {away_team} @ {home_team}: {len(home_players + away_players)} joueurs")
        except:
            continue
    
    print(f"\n   📊 Résultat: {games_with_data}/{len(games)} matchs ont des données")
    
except Exception as e:
    print(f"   ❌ Erreur: {e}")

print("\n" + "=" * 80)
print("✅ Tests terminés")
print("\n💡 CONCLUSION:")
print("   - L'API live.nba est conçue pour les données en temps réel")
print("   - Elle devrait donner accès aux stats dès la fin du match")
print("   - Structure différente de stats.endpoints (format JSON vs DataFrame)")

"""
🧪 Script de test : Scores Fantasy

Crée des données de test et teste les endpoints de scores/leaderboard
"""
import requests
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000/api/v1"

def print_section(title):
    print("\n" + "="*80)
    print(title)
    print("="*80)

def main():
    # CONNEXION
    print_section("🔐 Connexion")
    
    login_response = requests.post(
        f"{BASE_URL}/auth/connexion",
        json={"nom_utilisateur": "testuser", "mot_de_passe": "testpassword123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Échec de connexion : {login_response.json()}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Connecté")
    
    team_id = 2
    
    # TEST 1 : Historique des scores
    print_section("📊 TEST 1 : Historique des scores (7 derniers jours)")
    
    response = requests.get(
        f"{BASE_URL}/teams/{team_id}/scores",
        headers=headers,
        params={"days": 7}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Équipe: {data['team']['name']}")
        print(f"   Période: {data['period']['start_date']} → {data['period']['end_date']}")
        print(f"\n   📈 Statistiques:")
        print(f"      Score total: {data['statistics']['total_score']} pts")
        print(f"      Score moyen: {data['statistics']['average_score']} pts/jour")
        print(f"      Matchs joués: {data['statistics']['games_played']}")
        
        if data['statistics']['best_day']['date']:
            print(f"      Meilleur jour: {data['statistics']['best_day']['date']} ({data['statistics']['best_day']['score']} pts)")
            print(f"      Pire jour: {data['statistics']['worst_day']['date']} ({data['statistics']['worst_day']['score']} pts)")
        
        if data['daily_scores']:
            print(f"\n   📅 Scores quotidiens:")
            for day in data['daily_scores'][:5]:  # Afficher les 5 derniers
                print(f"      {day['date']}: {day['total_score']} pts")
        else:
            print(f"\n   ⚠️ Aucun score enregistré")
    else:
        print(f"❌ Erreur: {response.json()}")
    
    # TEST 2 : Détail d'un jour spécifique
    print_section("📊 TEST 2 : Détail d'un jour spécifique")
    
    # Essayer hier
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    response = requests.get(
        f"{BASE_URL}/teams/{team_id}/scores/{yesterday}",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Date: {yesterday}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ {data['team']['name']}")
        print(f"   Score total: {data['total_score']} pts")
        print(f"\n   👥 Détail des joueurs:")
        
        for player in data['player_scores']:
            if player['played']:
                print(f"      ✅ {player['position_slot']:4} | {player['player']['full_name']:25} | {player['fantasy_score']:5.1f} pts")
                print(f"         Stats: {player['stats']['points']} PTS, {player['stats']['rebounds']} REB, {player['stats']['assists']} AST")
            else:
                print(f"      ❌ {player['position_slot']:4} | {player['player']['full_name']:25} | DNP (repos/blessé)")
    
    elif response.status_code == 404:
        print(f"⚠️ Aucun score trouvé pour cette date")
        print(f"   Il n'y a peut-être pas encore de données (worker pas encore exécuté)")
    else:
        print(f"❌ Erreur: {response.json()}")
    
    # TEST 3 : Leaderboard SOLO
    print_section("🏆 TEST 3 : Classement de la ligue SOLO")
    
    response = requests.get(
        f"{BASE_URL}/leagues/solo/leaderboard",
        params={"limit": 10}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n🏆 {data['league']['name']}")
        print(f"   Type: {data['league']['type']}")
        print(f"   Période: {data['period']['description']}")
        print(f"   Total équipes: {data['total_teams']}")
        
        if data['leaderboard']:
            print(f"\n   📊 TOP {len(data['leaderboard'])} :")
            print("   " + "-"*70)
            
            for team in data['leaderboard']:
                rank = team['rank']
                medal = ""
                if rank == 1:
                    medal = "🥇"
                elif rank == 2:
                    medal = "🥈"
                elif rank == 3:
                    medal = "🥉"
                
                print(f"   {medal} #{rank:<2} | {team['team_name']:30} | {team['total_score']:>7.1f} pts ({team['games_played']} jours, moy. {team['average_score']:.1f})")
        else:
            print(f"\n   ⚠️ Aucune équipe dans le classement (pas encore de scores)")
    else:
        print(f"❌ Erreur: {response.json()}")
    
    # TEST 4 : Leaderboard d'une ligue spécifique
    print_section("🏆 TEST 4 : Classement d'une ligue spécifique (ID=1)")
    
    response = requests.get(
        f"{BASE_URL}/leagues/1/leaderboard",
        params={"limit": 20}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['league']['name']} ({data['league']['type']})")
        print(f"   Équipes affichées: {data['displayed_teams']}/{data['total_teams']}")
    else:
        print(f"❌ Erreur: {response.json()}")
    
    # RÉSUMÉ
    print_section("✅ TESTS TERMINÉS")
    
    print("""
   📊 Endpoints testés :
      - GET /teams/{id}/scores (historique)
      - GET /teams/{id}/scores/{date} (détail quotidien)
      - GET /leagues/solo/leaderboard (classement SOLO)
      - GET /leagues/{id}/leaderboard (classement général)
   
   ⚠️ NOTE :
   Les scores fantasy nécessitent que le worker ait été exécuté.
   Si aucun score n'apparaît, c'est normal : le worker récupère les
   boxscores NBA quotidiennement à 8h du matin.
   
   Pour tester avec des données, lancez manuellement :
      python backend/app/worker/tasks/fetch_boxscores.py
    """)

if __name__ == "__main__":
    main()

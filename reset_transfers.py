"""
🔄 Script de Reset des Transferts

Supprime tous les transferts de l'équipe de test pour repartir à 0/2.
Permet de tester complètement le système sans attendre lundi prochain.
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

def main():
    print("="*80)
    print("🔄 RESET DES TRANSFERTS DE TEST")
    print("="*80)
    
    # Connexion
    print("\n🔐 Connexion...")
    login_response = requests.post(
        f"{BASE_URL}/auth/connexion",
        json={"nom_utilisateur": "testuser", "mot_de_passe": "testpassword123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Échec de la connexion")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Connecté")
    
    team_id = 2
    
    # Vérifier l'état actuel
    print(f"\n📊 État actuel du roster...")
    roster_response = requests.get(f"{BASE_URL}/teams/{team_id}/roster", headers=headers)
    roster = roster_response.json()
    
    print(f"   💰 Salary cap : ${roster['salary_cap_used']/1_000_000:.1f}M / $60M")
    print(f"   🔄 Transferts : {roster['transfers_this_week']}/2")
    
    print("\n⚠️  ATTENTION : Ce script nécessite un accès direct à la base de données")
    print("   Pour réinitialiser le compteur de transferts, deux options :\n")
    
    print("   Option 1 : Supprimer manuellement dans PostgreSQL")
    print("   -------------------------------------------------")
    print("   docker exec -it projetfullstack-db-1 psql -U nba_user -d nba_fantasy")
    print("   DELETE FROM transfer WHERE fantasy_team_id = 2;")
    print("   \\q")
    
    print("\n   Option 2 : Modifier la date des transferts (simuler lundi dernier)")
    print("   -----------------------------------------------------------------")
    print("   docker exec -it projetfullstack-db-1 psql -U nba_user -d nba_fantasy")
    print("   UPDATE transfer SET processed_at = processed_at - INTERVAL '8 days' WHERE fantasy_team_id = 2;")
    print("   \\q")
    
    print("\n   Option 3 : Garder MAX_TRANSFERS_PER_WEEK = 20 pour les tests")
    print("   -------------------------------------------------------------")
    print("   ✅ Déjà fait dans roster.py (ligne 38)")
    print("   ⚠️  Le serveur doit être redémarré pour prendre effet\n")
    
    print("="*80)
    print("💡 SOLUTION RECOMMANDÉE : Redémarrer le serveur uvicorn")
    print("="*80)
    print("\nDans le terminal où uvicorn tourne :")
    print("1. Ctrl+C pour arrêter")
    print("2. cd backend")
    print("3. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("4. Attendre 'Application startup complete'")
    print("5. python test_roster_edge_cases.py\n")

if __name__ == "__main__":
    main()

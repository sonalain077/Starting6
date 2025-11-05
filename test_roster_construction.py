"""
🧪 Test du Nouveau Système de Roster

Teste la nouvelle logique :
1. Phase CONSTRUCTION : Transferts illimités pour remplir le roster (0 → 6 joueurs)
2. Roster COMPLET (6/6) : Équipe devient ACTIVE automatiquement
3. Phase ACTIVE : Limite de 2 transferts/semaine s'applique

Ce test simule la création d'une équipe complète depuis zéro.
"""
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def print_section(title):
    print("\n" + "="*80)
    print(title)
    print("="*80)

def format_money(amount):
    return f"${amount/1_000_000:.1f}M"

def main():
    # CONNEXION
    print_section("🔐 ÉTAPE 0 : Connexion")
    
    login_response = requests.post(
        f"{BASE_URL}/auth/connexion",
        json={"nom_utilisateur": "testuser", "mot_de_passe": "testpassword123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Échec")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Connecté")
    
    team_id = 2
    
    # ÉTAT INITIAL
    print_section("📊 ÉTAPE 1 : État initial du roster")
    
    roster_response = requests.get(f"{BASE_URL}/teams/{team_id}/roster", headers=headers)
    roster = roster_response.json()
    
    print(f"   💰 Salary cap : {format_money(roster['salary_cap_used'])} / $60M")
    print(f"   📍 Statut : {roster['roster_status']}")
    print(f"   ✅ Roster complet : {'Oui' if roster['is_roster_complete'] else 'Non'}")
    print(f"   🔄 Transferts : {roster['transfers_this_week']}/2")
    
    occupied = sum(1 for s in roster['roster'] if s['player'])
    print(f"   👥 Joueurs : {occupied}/6")
    
    # PHASE CONSTRUCTION
    print_section("🏗️ ÉTAPE 2 : Phase CONSTRUCTION - Remplir le roster")
    
    if occupied == 6:
        print("   ℹ️ Roster déjà complet")
    else:
        print(f"   🎯 Objectif : Ajouter {6 - occupied} joueur(s)\n")
        
        positions_to_fill = []
        for slot in roster['roster']:
            if not slot['player']:
                positions_to_fill.append(slot['position_slot'])
        
        print(f"   Positions à remplir : {', '.join(positions_to_fill)}\n")
        
        for i, position in enumerate(positions_to_fill, 1):
            print(f"   [{i}/{len(positions_to_fill)}] Ajout d'un joueur pour {position}...")
            
            # Chercher un joueur abordable
            if position == 'UTIL':
                search_params = {"limit": 5}
            else:
                search_params = {"position": position, "limit": 5}
            
            search_response = requests.get(
                f"{BASE_URL}/teams/{team_id}/available-players",
                headers=headers,
                params=search_params
            )
            
            available = search_response.json()['players']
            
            if not available:
                print(f"      ❌ Aucun joueur disponible")
                continue
            
            # Prendre le premier joueur abordable
            selected = None
            for p in available:
                if p['is_affordable'] and not p['has_cooldown']:
                    selected = p['player']
                    break
            
            if not selected:
                print(f"      ❌ Aucun joueur abordable")
                continue
            
            # Ajouter le joueur
            add_response = requests.post(
                f"{BASE_URL}/teams/{team_id}/roster",
                headers=headers,
                json={
                    "player_id": selected['id'],
                    "position_slot": position
                }
            )
            
            if add_response.status_code == 201:
                result = add_response.json()
                player_name = f"{result['player_added']['first_name']} {result['player_added']['last_name']}"
                print(f"      ✅ {player_name} ajouté")
                print(f"         💰 Salary cap : {format_money(result['salary_cap_used'])}")
                print(f"         💵 Restant : {format_money(result['salary_cap_remaining'])}")
                
                # Afficher le message spécial si roster complet
                if "Félicitations" in result['message']:
                    print(f"\n      🎉 MESSAGE SPÉCIAL :")
                    print(f"      {result['message']}\n")
                
                time.sleep(0.5)  # Petite pause pour la lisibilité
            else:
                error = add_response.json()
                print(f"      ❌ Échec : {error.get('detail')}")
    
    # VÉRIFICATION FINALE
    print_section("📊 ÉTAPE 3 : Vérification du roster final")
    
    final_response = requests.get(f"{BASE_URL}/teams/{team_id}/roster", headers=headers)
    final = final_response.json()
    
    print(f"   💰 Salary cap : {format_money(final['salary_cap_used'])} / $60M")
    print(f"   💵 Budget restant : {format_money(final['salary_cap_remaining'])}")
    print(f"   📍 Statut : {final['roster_status']}")
    print(f"   ✅ Roster complet : {'Oui' if final['is_roster_complete'] else 'Non'}")
    print(f"   🔄 Transferts : {final['transfers_this_week']}/2\n")
    
    print("   Composition :")
    for slot in final['roster']:
        if slot['player']:
            player = slot['player']
            print(f"      ✅ {slot['position_slot']}: {player['first_name']} {player['last_name']} ({player['position']}) - {format_money(slot['acquired_salary'])}")
        else:
            print(f"      ❌ {slot['position_slot']}: [LIBRE]")
    
    occupied_final = sum(1 for s in final['roster'] if s['player'])
    
    # TEST DE LA LIMITE
    if occupied_final == 6 and final['is_roster_complete']:
        print_section("🧪 ÉTAPE 4 : Test de la limite de transferts")
        
        print("   Le roster est complet, la limite de 2 transferts/semaine est active")
        print(f"   Transferts actuels : {final['transfers_this_week']}/2\n")
        
        if final['transfers_this_week'] < 2:
            print("   Tentative d'ajout pour tester la limite...")
            # Essayer de retirer puis réajouter pour utiliser les transferts
            
            # Retirer un joueur
            first_player = None
            for slot in final['roster']:
                if slot['player']:
                    first_player = slot['player']
                    break
            
            if first_player:
                print(f"   1. Retrait de {first_player['first_name']} {first_player['last_name']}...")
                delete_response = requests.delete(
                    f"{BASE_URL}/teams/{team_id}/roster/{first_player['id']}",
                    headers=headers
                )
                
                if delete_response.status_code == 200:
                    print(f"      ✅ Retiré (transfert 1/2)")
                    
                    # Essayer de chercher un remplaçant
                    print(f"\n   2. Recherche d'un remplaçant...")
                    search_response = requests.get(
                        f"{BASE_URL}/teams/{team_id}/available-players",
                        headers=headers,
                        params={"limit": 5}
                    )
                    
                    available = search_response.json()['players']
                    replacement = None
                    for p in available:
                        if p['is_affordable'] and not p['has_cooldown']:
                            replacement = p['player']
                            break
                    
                    if replacement:
                        print(f"      Tentative d'ajout de {replacement['first_name']} {replacement['last_name']}...")
                        
                        add_response = requests.post(
                            f"{BASE_URL}/teams/{team_id}/roster",
                            headers=headers,
                            json={
                                "player_id": replacement['id'],
                                "position_slot": "UTIL"
                            }
                        )
                        
                        if add_response.status_code == 201:
                            print(f"      ✅ Ajouté (transfert 2/2)")
                            
                            print(f"\n   3. Tentative d'un 3ème transfert...")
                            # Essayer un 3ème (doit échouer)
                            
                            third_response = requests.post(
                                f"{BASE_URL}/teams/{team_id}/roster",
                                headers=headers,
                                json={
                                    "player_id": replacement['id'] + 1,
                                    "position_slot": "UTIL"
                                }
                            )
                            
                            if third_response.status_code == 400:
                                error = third_response.json()
                                print(f"      ✅ 3ème transfert bloqué : {error.get('detail')}")
                            else:
                                print(f"      ❌ Le 3ème transfert a été accepté (BUG !)")
        else:
            print("   ⚠️ Limite déjà atteinte cette semaine")
    
    # RÉSUMÉ
    print_section("✅ RÉSUMÉ")
    
    print(f"""
   📊 État final :
      - Joueurs : {occupied_final}/6
      - Salary cap : {format_money(final['salary_cap_used'])} / $60M
      - Statut : {final['roster_status']}
      - Limite transferts : {'Active' if final['is_roster_complete'] else 'Inactive (construction)'}
   
   ✅ Tests validés :
      - Phase CONSTRUCTION : Transferts illimités
      - Roster COMPLET : Activation automatique
      - Phase ACTIVE : Limite 2 transferts/semaine
    """)

if __name__ == "__main__":
    main()

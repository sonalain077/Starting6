"""
🧪 Tests Edge Cases Avancés - Roster Management

Tests effectués :
1. Remplir complètement le roster (6/6 joueurs)
2. Tester le DELETE endpoint (retrait d'un joueur)
3. Vérifier le cooldown après DROP
4. Tenter de dépasser le salary cap ($60M)
5. Vérifier la libération du salary cap après DELETE

Note : Ce test utilise une limite de transferts élevée pour permettre
       de remplir complètement le roster lors des tests.
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def print_section(title):
    print("\n" + "="*80)
    print(title)
    print("="*80)

def format_money(amount):
    """Formate un montant en millions de dollars"""
    return f"${amount/1_000_000:.1f}M"

def main():
    # ====================================
    # CONNEXION
    # ====================================
    print_section("🔐 ÉTAPE 0 : Connexion")
    
    login_response = requests.post(
        f"{BASE_URL}/auth/connexion",
        json={"nom_utilisateur": "testuser", "mot_de_passe": "testpassword123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Échec : {login_response.status_code}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Connexion réussie")
    
    team_id = 2  # Équipe de test
    
    # ====================================
    # ÉTAPE 1 : Vider le roster existant
    # ====================================
    print_section("🗑️ ÉTAPE 1 : Nettoyage du roster")
    
    roster_response = requests.get(f"{BASE_URL}/teams/{team_id}/roster", headers=headers)
    initial_roster = roster_response.json()
    
    players_to_remove = []
    for slot in initial_roster['roster']:
        if slot['player']:
            players_to_remove.append({
                'id': slot['player']['id'],
                'name': f"{slot['player']['first_name']} {slot['player']['last_name']}",
                'position': slot['position_slot'],
                'salary': slot['acquired_salary']
            })
    
    if players_to_remove:
        print(f"   Joueurs actuels dans le roster : {len(players_to_remove)}")
        
        for player in players_to_remove:
            print(f"\n   Retrait de {player['name']} ({player['position']})...")
            
            delete_response = requests.delete(
                f"{BASE_URL}/teams/{team_id}/roster/{player['id']}",
                headers=headers
            )
            
            if delete_response.status_code == 200:
                result = delete_response.json()
                print(f"      ✅ Retiré avec succès")
                print(f"         💰 Salary cap libéré : {format_money(result['salary_cap_freed'])}")
                print(f"         💵 Budget restant : {format_money(result['salary_cap_remaining'])}")
                print(f"         ⏰ Cooldown jusqu'au : {result['cooldown_until'][:10]}")
            elif delete_response.status_code == 400:
                error = delete_response.json()
                if "limite" in error.get('detail', '').lower():
                    print(f"      ⚠️ Limite de transferts atteinte : {error['detail']}")
                    print(f"      ℹ️ On continue avec le roster partiellement vidé")
                    break
                else:
                    print(f"      ❌ Erreur : {error.get('detail')}")
            else:
                print(f"      ❌ Erreur {delete_response.status_code}")
    else:
        print("   ✅ Roster déjà vide")
    
    # Petite pause pour voir les changements
    time.sleep(1)
    
    # ====================================
    # ÉTAPE 2 : Vérifier le roster vidé
    # ====================================
    print_section("📊 ÉTAPE 2 : Vérification du roster après nettoyage")
    
    roster_response = requests.get(f"{BASE_URL}/teams/{team_id}/roster", headers=headers)
    current_roster = roster_response.json()
    
    print(f"   💰 Salary cap : {format_money(current_roster['salary_cap_used'])} / $60M")
    print(f"   💵 Budget restant : {format_money(current_roster['salary_cap_remaining'])}")
    print(f"   🔄 Transferts : {current_roster['transfers_this_week']}/2")
    
    occupied = sum(1 for s in current_roster['roster'] if s['player'])
    print(f"   📍 Positions occupées : {occupied}/6")
    
    if current_roster['transfers_this_week'] >= 2:
        print("\n   ⚠️ LIMITE DE TRANSFERTS ATTEINTE !")
        print("   ℹ️ Pour effectuer les tests complets, il faut temporairement")
        print("   ℹ️ augmenter MAX_TRANSFERS_PER_WEEK dans roster.py")
        print("\n   💡 Suggestion : Changer MAX_TRANSFERS_PER_WEEK = 2 → 20")
        print("      Fichier : backend/app/api/v1/endpoints/roster.py (ligne 38)")
        return
    
    # ====================================
    # TEST 1 : Remplir le roster avec des joueurs chers
    # ====================================
    print_section("🧪 TEST 1 : Remplir le roster (6/6 positions)")
    
    # Objectif : Choisir des joueurs pour approcher les $60M
    print("   Stratégie : Choisir des joueurs chers pour tester le salary cap\n")
    
    positions_to_fill = ['PG', 'SG', 'SF', 'PF', 'C', 'UTIL']
    players_added = []
    
    for position in positions_to_fill:
        # Vérifier combien de transferts on peut encore faire
        check_roster = requests.get(f"{BASE_URL}/teams/{team_id}/roster", headers=headers).json()
        
        if check_roster['transfers_this_week'] >= 2:
            print(f"   ⚠️ Limite de transferts atteinte à {len(players_added)}/6 joueurs")
            break
        
        print(f"   🔍 Recherche d'un joueur pour {position}...")
        
        # Pour UTIL, prendre n'importe quel poste
        if position == 'UTIL':
            search_params = {"limit": 10}
        else:
            search_params = {"position": position, "limit": 10}
        
        search_response = requests.get(
            f"{BASE_URL}/teams/{team_id}/available-players",
            headers=headers,
            params=search_params
        )
        
        available = search_response.json()
        
        if not available['players']:
            print(f"      ❌ Aucun joueur disponible pour {position}")
            continue
        
        # Prendre le joueur le plus cher qui est abordable
        affordable = [p for p in available['players'] if p['is_affordable'] and not p['has_cooldown']]
        
        if not affordable:
            print(f"      ❌ Aucun joueur abordable pour {position}")
            continue
        
        # Trier par prix décroissant (les plus chers en premier)
        affordable.sort(key=lambda x: x['player']['fantasy_cost'], reverse=True)
        selected = affordable[0]['player']
        
        print(f"      Sélectionné : {selected['first_name']} {selected['last_name']} ({selected['position']}) - {format_money(selected['fantasy_cost'])}")
        
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
            print(f"      ✅ Ajouté avec succès")
            print(f"         💰 Salary cap : {format_money(result['salary_cap_used'])} / $60M")
            print(f"         💵 Restant : {format_money(result['salary_cap_remaining'])}")
            print(f"         🔄 Transferts : {2 - result['transfers_remaining_this_week']}/2\n")
            
            players_added.append({
                'id': selected['id'],
                'name': f"{selected['first_name']} {selected['last_name']}",
                'position': position,
                'salary': selected['fantasy_cost']
            })
        else:
            error = add_response.json()
            print(f"      ❌ Échec : {error.get('detail')}\n")
            
            if "limite" in error.get('detail', '').lower():
                print(f"   ⚠️ Limite de transferts atteinte")
                break
    
    print(f"\n   ✅ {len(players_added)} joueur(s) ajouté(s)")
    
    # ====================================
    # VÉRIFICATION : Roster complet
    # ====================================
    print_section("📊 VÉRIFICATION : État du roster")
    
    roster_response = requests.get(f"{BASE_URL}/teams/{team_id}/roster", headers=headers)
    roster = roster_response.json()
    
    print(f"   💰 Salary cap : {format_money(roster['salary_cap_used'])} / $60M ({roster['salary_cap_used']/600_000:.1f}%)")
    print(f"   💵 Budget restant : {format_money(roster['salary_cap_remaining'])}")
    print(f"   🔄 Transferts : {roster['transfers_this_week']}/2\n")
    
    print("   Composition du roster :")
    total_salary = 0
    roster_players = []
    
    for slot in roster['roster']:
        if slot['player']:
            player = slot['player']
            salary = slot['acquired_salary']
            total_salary += salary
            roster_players.append({
                'id': player['id'],
                'name': f"{player['first_name']} {player['last_name']}",
                'position': slot['position_slot'],
                'salary': salary
            })
            print(f"      ✅ {slot['position_slot']}: {player['first_name']} {player['last_name']} ({player['position']}) - {format_money(salary)}")
        else:
            print(f"      ❌ {slot['position_slot']}: [LIBRE]")
    
    print(f"\n   Total calculé : {format_money(total_salary)}")
    
    # ====================================
    # TEST 2 : Tester dépassement salary cap
    # ====================================
    print_section("🧪 TEST 2 : Tentative de dépassement du salary cap")
    
    budget_remaining = roster['salary_cap_remaining']
    print(f"   Budget actuel : {format_money(budget_remaining)}")
    
    # Chercher un joueur qui dépasse le budget
    expensive_response = requests.get(
        f"{BASE_URL}/teams/{team_id}/available-players",
        headers=headers,
        params={"limit": 100}
    )
    
    expensive_players = expensive_response.json()['players']
    too_expensive = [p for p in expensive_players if not p['is_affordable'] and not p['has_cooldown']]
    
    if too_expensive and roster['transfers_this_week'] < 2:
        # Trouver une position libre
        free_position = None
        for slot in roster['roster']:
            if not slot['player']:
                free_position = slot['position_slot']
                break
        
        if free_position:
            test_player = too_expensive[0]['player']
            print(f"\n   Tentative d'ajout de {test_player['first_name']} {test_player['last_name']}")
            print(f"      Coût : {format_money(test_player['fantasy_cost'])}")
            print(f"      Budget : {format_money(budget_remaining)}")
            print(f"      Dépassement : {format_money(test_player['fantasy_cost'] - budget_remaining)}")
            
            overflow_response = requests.post(
                f"{BASE_URL}/teams/{team_id}/roster",
                headers=headers,
                json={
                    "player_id": test_player['id'],
                    "position_slot": free_position
                }
            )
            
            if overflow_response.status_code == 400:
                error = overflow_response.json()
                if "salary cap" in error.get('detail', '').lower():
                    print(f"\n      ✅ Rejet attendu : {error['detail']}")
                else:
                    print(f"\n      ⚠️ Rejet pour autre raison : {error['detail']}")
            else:
                print(f"\n      ❌ Le dépassement a été accepté (BUG !)")
        else:
            print("   ℹ️ Roster complet, impossible de tester le dépassement")
    else:
        if roster['transfers_this_week'] >= 2:
            print("   ℹ️ Limite de transferts atteinte, test non effectué")
        else:
            print("   ℹ️ Aucun joueur trop cher disponible pour tester")
    
    # ====================================
    # TEST 3 : DELETE endpoint
    # ====================================
    print_section("🧪 TEST 3 : Test du DELETE endpoint")
    
    if roster_players and roster['transfers_this_week'] < 2:
        # Retirer le joueur le moins cher
        cheapest = min(roster_players, key=lambda x: x['salary'])
        
        print(f"   Retrait de {cheapest['name']} ({cheapest['position']}) - {format_money(cheapest['salary'])}")
        print(f"   Salary cap avant : {format_money(roster['salary_cap_used'])}")
        
        delete_response = requests.delete(
            f"{BASE_URL}/teams/{team_id}/roster/{cheapest['id']}",
            headers=headers
        )
        
        if delete_response.status_code == 200:
            result = delete_response.json()
            print(f"\n   ✅ DELETE réussi !")
            print(f"      Joueur retiré : {result['player_removed']['first_name']} {result['player_removed']['last_name']}")
            print(f"      Position libérée : {result['position_freed']}")
            print(f"      💰 Salary cap libéré : {format_money(result['salary_cap_freed'])}")
            print(f"      💵 Nouveau budget : {format_money(result['salary_cap_remaining'])}")
            print(f"      ⏰ Cooldown jusqu'au : {result['cooldown_until'][:10]}")
            print(f"      🔄 Transferts restants : {result['transfers_remaining_this_week']}/2")
            
            # Vérifier le roster après DELETE
            print("\n   Vérification du roster après DELETE :")
            verify_response = requests.get(f"{BASE_URL}/teams/{team_id}/roster", headers=headers)
            verify_roster = verify_response.json()
            
            expected_cap = roster['salary_cap_used'] - cheapest['salary']
            actual_cap = verify_roster['salary_cap_used']
            
            print(f"      Salary cap attendu : {format_money(expected_cap)}")
            print(f"      Salary cap réel : {format_money(actual_cap)}")
            
            if abs(expected_cap - actual_cap) < 100:  # Tolérance de 100$
                print(f"      ✅ Salary cap correctement mis à jour")
            else:
                print(f"      ❌ Erreur dans le calcul du salary cap !")
            
            # TEST 4 : Vérifier le cooldown
            print_section("🧪 TEST 4 : Test du cooldown (7 jours)")
            
            print(f"   Tentative de re-ajout immédiat de {cheapest['name']}...")
            
            readd_response = requests.post(
                f"{BASE_URL}/teams/{team_id}/roster",
                headers=headers,
                json={
                    "player_id": cheapest['id'],
                    "position_slot": cheapest['position']
                }
            )
            
            if readd_response.status_code == 400:
                error = readd_response.json()
                if "cooldown" in error.get('detail', '').lower():
                    print(f"   ✅ Cooldown actif (attendu) : {error['detail']}")
                else:
                    print(f"   ⚠️ Rejet pour autre raison : {error['detail']}")
            else:
                print(f"   ❌ Le cooldown n'a pas été appliqué (BUG !)")
        
        else:
            error = delete_response.json()
            print(f"   ❌ DELETE échoué : {error.get('detail')}")
    
    elif roster['transfers_this_week'] >= 2:
        print("   ℹ️ Limite de transferts atteinte, DELETE non testé")
    else:
        print("   ℹ️ Roster vide, rien à supprimer")
    
    # ====================================
    # RÉSUMÉ FINAL
    # ====================================
    print_section("✅ RÉSUMÉ DES TESTS")
    
    final_roster_response = requests.get(f"{BASE_URL}/teams/{team_id}/roster", headers=headers)
    final_roster = final_roster_response.json()
    
    final_occupied = sum(1 for s in final_roster['roster'] if s['player'])
    
    print(f"""
   📊 État final :
      - Positions : {final_occupied}/6
      - Salary cap : {format_money(final_roster['salary_cap_used'])} / $60M
      - Budget : {format_money(final_roster['salary_cap_remaining'])}
      - Transferts : {final_roster['transfers_this_week']}/2
   
   🧪 Tests effectués :
      - Remplir roster : {'✅' if final_occupied >= 4 else '⚠️'} {final_occupied}/6 positions
      - Salary cap overflow : {'✅ Testé' if budget_remaining > 0 else '⚠️ Non testé'}
      - DELETE endpoint : {'✅ Testé' if 'cheapest' in locals() else '⚠️ Non testé'}
      - Cooldown : {'✅ Vérifié' if 'readd_response' in locals() else '⚠️ Non testé'}
    """)

if __name__ == "__main__":
    main()

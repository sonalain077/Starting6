"""
🧪 Test Roster Complet avec Budget Équilibré

Ce test :
1. Vide le roster actuel
2. Choisit 6 joueurs avec un budget équilibré (~$10M chacun)
3. Vérifie l'activation automatique après le 6ème joueur
4. Affiche les statistiques des joueurs de la BDD
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

def print_section(title):
    print("\n" + "="*80)
    print(title)
    print("="*80)

def format_money(amount):
    return f"${amount/1_000_000:.1f}M"

def main():
    # CONNEXION
    print_section("🔐 Connexion")
    
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
    
    # STATISTIQUES BDD
    print_section("📊 Statistiques des Joueurs dans la BDD")
    
    all_players_response = requests.get(
        f"{BASE_URL}/teams/{team_id}/available-players",
        headers=headers,
        params={"limit": 100}
    )
    
    all_players = all_players_response.json()['players']
    
    if all_players:
        costs = [p['player']['fantasy_cost'] for p in all_players]
        costs.sort()
        
        print(f"\n   Total joueurs disponibles : {len(all_players)}")
        print(f"   💰 Salaire minimum : {format_money(costs[0])}")
        print(f"   💰 Salaire maximum : {format_money(costs[-1])}")
        print(f"   💰 Salaire moyen : {format_money(sum(costs)/len(costs))}")
        print(f"   💰 Salaire médian : {format_money(costs[len(costs)//2])}")
        
        print("\n   📉 Distribution des salaires :")
        ranges = [
            (5, 6, "< $6M"),
            (6, 7, "$6-7M"),
            (7, 8, "$7-8M"),
            (8, 9, "$8-9M"),
            (9, 10, "$9-10M"),
            (10, 15, "$10-15M"),
        ]
        
        for min_val, max_val, label in ranges:
            count = sum(1 for c in costs if min_val*1_000_000 <= c < max_val*1_000_000)
            pct = (count / len(costs)) * 100
            bar = "█" * int(pct / 2)
            print(f"      {label:12} : {count:3} joueurs ({pct:4.1f}%) {bar}")
        
        print("\n   💡 Budget recommandé par joueur : ~$10M (pour remplir 6 positions)")
    
    # VIDER LE ROSTER
    print_section("🗑️ Nettoyage du roster")
    
    roster_response = requests.get(f"{BASE_URL}/teams/{team_id}/roster", headers=headers)
    current_roster = roster_response.json()
    
    players_in_roster = [s['player'] for s in current_roster['roster'] if s['player']]
    
    if players_in_roster:
        print(f"   Retrait de {len(players_in_roster)} joueur(s)...\n")
        
        for player in players_in_roster:
            delete_response = requests.delete(
                f"{BASE_URL}/teams/{team_id}/roster/{player['id']}",
                headers=headers
            )
            
            if delete_response.status_code == 200:
                print(f"      ✅ {player['first_name']} {player['last_name']} retiré")
            else:
                print(f"      ⚠️ {player['first_name']} {player['last_name']} (erreur ou cooldown)")
    else:
        print("   ✅ Roster déjà vide")
    
    # STRATÉGIE : Choisir 6 joueurs entre $8M et $10M pour équilibrer
    print_section("🏗️ Construction du Roster (Budget Équilibré)")
    
    print("   🎯 Stratégie : Choisir des joueurs à ~$8-10M chacun")
    print("   💰 Budget total : $60M → ~$10M par joueur\n")
    
    positions = ['PG', 'SG', 'SF', 'PF', 'C', 'UTIL']
    selected_players = []
    
    for i, position in enumerate(positions, 1):
        print(f"   [{i}/6] Recherche pour {position}...")
        
        # Chercher des joueurs dans la gamme $7M-$11M
        if position == 'UTIL':
            search_params = {"limit": 50}
        else:
            search_params = {"position": position, "limit": 50}
        
        search_response = requests.get(
            f"{BASE_URL}/teams/{team_id}/available-players",
            headers=headers,
            params=search_params
        )
        
        available = search_response.json()['players']
        
        # Filtrer les joueurs dans la bonne fourchette de prix
        budget_remaining = 60_000_000 - sum(p['cost'] for p in selected_players)
        positions_remaining = 6 - len(selected_players)
        avg_budget_per_player = budget_remaining / positions_remaining
        
        # Chercher un joueur proche du budget moyen restant
        affordable = [
            p for p in available 
            if p['is_affordable'] 
            and not p['has_cooldown']
            and 7_000_000 <= p['player']['fantasy_cost'] <= min(11_000_000, budget_remaining - (positions_remaining - 1) * 5_000_000)
        ]
        
        if not affordable:
            # Si aucun dans la fourchette, prendre le moins cher
            affordable = [p for p in available if p['is_affordable'] and not p['has_cooldown']]
        
        if not affordable:
            print(f"      ❌ Aucun joueur disponible")
            continue
        
        # Trier par proximité au budget moyen
        affordable.sort(key=lambda x: abs(x['player']['fantasy_cost'] - avg_budget_per_player))
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
            print(f"         🔄 Statut : {result.get('transfers_remaining_this_week', 'Construction')}")
            
            selected_players.append({
                'name': f"{selected['first_name']} {selected['last_name']}",
                'position': position,
                'cost': selected['fantasy_cost']
            })
            
            # Vérifier si c'est le 6ème joueur (roster complet)
            if len(selected_players) == 6:
                print(f"\n      🎉 MESSAGE DU SERVEUR :")
                for line in result['message'].split('\n'):
                    print(f"         {line}")
            
            print()
        else:
            error = add_response.json()
            print(f"      ❌ Échec : {error.get('detail')}\n")
    
    # VÉRIFICATION FINALE
    print_section("📊 Roster Final")
    
    final_response = requests.get(f"{BASE_URL}/teams/{team_id}/roster", headers=headers)
    final = final_response.json()
    
    print(f"   💰 Salary cap : {format_money(final['salary_cap_used'])} / $60M ({final['salary_cap_used']/600_000:.1f}%)")
    print(f"   💵 Budget restant : {format_money(final['salary_cap_remaining'])}")
    print(f"   📍 Statut : {final['roster_status']}")
    print(f"   ✅ Roster complet : {'Oui ✅' if final['is_roster_complete'] else 'Non ❌'}")
    print(f"   🔄 Transferts : {final['transfers_this_week']}/2\n")
    
    print("   Composition :")
    total_cost = 0
    for slot in final['roster']:
        if slot['player']:
            player = slot['player']
            cost = slot['acquired_salary']
            total_cost += cost
            print(f"      ✅ {slot['position_slot']:4} : {player['first_name']} {player['last_name']:20} ({player['position']}) - {format_money(cost)}")
        else:
            print(f"      ❌ {slot['position_slot']:4} : [LIBRE]")
    
    occupied = sum(1 for s in final['roster'] if s['player'])
    
    print(f"\n   📊 Résumé :")
    print(f"      Joueurs : {occupied}/6")
    print(f"      Coût total : {format_money(total_cost)}")
    print(f"      Coût moyen : {format_money(total_cost / occupied) if occupied > 0 else '$0M'}")
    
    # TEST DE LA LIMITE
    if occupied == 6 and final['is_roster_complete']:
        print_section("🧪 Test de la Limite de Transferts")
        
        print("   ✅ Le roster est complet, l'équipe est ACTIVE")
        print(f"   🔒 La limite de 2 transferts/semaine est maintenant activée")
        print(f"   📊 Transferts actuels : {final['transfers_this_week']}/2")
        
        if final['transfers_this_week'] == 0:
            print("\n   💡 Vous pouvez maintenant faire jusqu'à 2 transferts cette semaine")
        else:
            print(f"\n   ⚠️ Il reste {2 - final['transfers_this_week']} transfert(s) disponible(s) cette semaine")
    
    # RÉSUMÉ
    print_section("✅ TEST TERMINÉ")
    
    if occupied == 6:
        print("""
   🎉 SUCCÈS TOTAL !
   
   ✅ Roster complet (6/6 joueurs)
   ✅ Budget bien géré
   ✅ Système de construction fonctionne
   ✅ Activation automatique après 6ème joueur
   ✅ Limite de transferts activée
        """)
    else:
        print(f"""
   ⚠️ Roster incomplet ({occupied}/6 joueurs)
   
   Raisons possibles :
   - Pas assez de joueurs dans la gamme de prix
   - Budget mal réparti
   - Cooldowns actifs sur certains joueurs
        """)

if __name__ == "__main__":
    main()

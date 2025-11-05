"""
Test des endpoints Roster
Scénario complet : créer une équipe puis ajouter des joueurs
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# ========================================
# 0. INSCRIPTION (Si l'utilisateur n'existe pas)
# ========================================
print("=" * 80)
print("🔐 ÉTAPE 0 : Inscription (si nécessaire)")
print("=" * 80)

signup_data = {
    "nom_utilisateur": "testuser",
    "mot_de_passe": "testpassword123"
}

response = requests.post(f"{BASE_URL}/auth/inscription", json=signup_data)
if response.status_code == 201:
    print(f"✅ Nouvel utilisateur créé : testuser")
elif response.status_code == 400:
    print(f"ℹ️  L'utilisateur existe déjà, passage à la connexion")
else:
    print(f"⚠️  Réponse inscription : {response.status_code}")

# ========================================
# 1. CONNEXION
# ========================================
print("\n" + "=" * 80)
print("🔐 ÉTAPE 1 : Connexion")
print("=" * 80)

login_data = {
    "nom_utilisateur": "testuser",
    "mot_de_passe": "testpassword123"
}

response = requests.post(f"{BASE_URL}/auth/connexion", json=login_data)
if response.status_code == 200:
    token = response.json()["access_token"]
    print(f"✅ Connexion réussie ! Token obtenu")
    headers = {"Authorization": f"Bearer {token}"}
else:
    print(f"❌ Erreur connexion : {response.status_code}")
    print(response.json())
    exit(1)

# ========================================
# 2. RÉCUPÉRER LA LIGUE SOLO
# ========================================
print("\n" + "=" * 80)
print("🏆 ÉTAPE 2 : Récupération de la ligue SOLO")
print("=" * 80)

response = requests.get(f"{BASE_URL}/leagues/solo", headers=headers)
if response.status_code == 200:
    solo_league = response.json()
    print(f"✅ Ligue SOLO trouvée : {solo_league['name']} (ID: {solo_league['id']})")
    league_id = solo_league["id"]
else:
    print(f"❌ Erreur : {response.status_code}")
    print(response.json())
    exit(1)

# ========================================
# 3. CRÉER UNE ÉQUIPE (si pas déjà faite)
# ========================================
print("\n" + "=" * 80)
print("🏀 ÉTAPE 3 : Création d'une équipe de test")
print("=" * 80)

# D'abord vérifier si on a déjà une équipe
response = requests.get(f"{BASE_URL}/teams/me", headers=headers)
if response.status_code == 200:
    teams = response.json()
    if teams:
        team = teams[0]
        print(f"✅ Équipe existante trouvée : {team['name']} (ID: {team['id']})")
        team_id = team["id"]
    else:
        # Créer une nouvelle équipe
        team_data = {
            "name": "Test Roster Team",
            "league_id": league_id
        }
        response = requests.post(f"{BASE_URL}/teams", json=team_data, headers=headers)
        if response.status_code == 201:
            team = response.json()
            print(f"✅ Équipe créée : {team['name']} (ID: {team['id']})")
            team_id = team["id"]
        else:
            print(f"❌ Erreur création équipe : {response.status_code}")
            print(response.json())
            exit(1)
else:
    print(f"❌ Erreur : {response.status_code}")
    exit(1)

# ========================================
# 4. AFFICHER LE ROSTER ACTUEL (vide)
# ========================================
print("\n" + "=" * 80)
print("👥 ÉTAPE 4 : Affichage du roster actuel")
print("=" * 80)

response = requests.get(f"{BASE_URL}/teams/{team_id}/roster", headers=headers)
if response.status_code == 200:
    roster = response.json()
    print(f"✅ Roster de '{roster['team_name']}' :")
    print(f"   💰 Salary cap utilisé : ${roster['salary_cap_used']/1_000_000:.1f}M / $60M")
    print(f"   💵 Budget restant : ${roster['salary_cap_remaining']/1_000_000:.1f}M")
    print(f"   🔄 Transferts cette semaine : {roster['transfers_this_week']}/2")
    print(f"\n   Positions :")
    for slot in roster['roster']:
        if slot['player']:
            print(f"      {slot['position_slot']} : {slot['player']['full_name']} (${slot['acquired_salary']/1_000_000:.1f}M)")
        else:
            print(f"      {slot['position_slot']} : [LIBRE]")
else:
    print(f"❌ Erreur GET roster : {response.status_code}")
    print(f"   Réponse brute : {response.text[:500] if response.text else 'Vide'}")
    try:
        print(response.json())
    except:
        pass
    exit(1)

# ========================================
# 5. LISTER LES JOUEURS DISPONIBLES
# ========================================
print("\n" + "=" * 80)
print("📋 ÉTAPE 5 : Liste des joueurs disponibles")
print("=" * 80)

response = requests.get(
    f"{BASE_URL}/teams/{team_id}/available-players",
    headers=headers,
    params={"limit": 10}  # Top 10 seulement
)
if response.status_code == 200:
    available = response.json()
    print(f"✅ {available['total_count']} joueurs disponibles")
    print(f"   💵 Budget restant : ${available['salary_cap_remaining']/1_000_000:.1f}M")
    print(f"   📍 Positions libres : {', '.join(available['available_positions'])}")
    print(f"\n   Top 10 joueurs :")
    for i, ap in enumerate(available['players'][:10], 1):
        player = ap['player']
        affordable = "✅" if ap['is_affordable'] else "❌"
        cooldown = " [COOLDOWN]" if ap['has_cooldown'] else ""
        # Debug: check player structure
        if i == 1:
            print(f"      DEBUG: player keys = {list(player.keys())}")
        print(f"      {i}. {player.get('full_name', 'N/A')} ({player.get('position', 'N/A')}) - ${player.get('fantasy_cost', 0)/1_000_000:.1f}M {affordable}{cooldown}")
else:
    print(f"❌ Erreur : {response.status_code}")
    print(response.json())
    exit(1)

# ========================================
# 6. AJOUTER UN JOUEUR AU ROSTER
# ========================================
print("\n" + "=" * 80)
print("➕ ÉTAPE 6 : Ajout d'un joueur au roster")
print("=" * 80)

# Prendre le premier joueur disponible et abordable
first_player = None
for ap in available['players']:
    if ap['is_affordable'] and not ap['has_cooldown']:
        first_player = ap['player']
        break

if first_player:
    print(f"   Tentative d'ajout : {first_player['full_name']} ({first_player['position']})")
    
    add_data = {
        "player_id": first_player['id'],
        "position_slot": first_player['position']  # Utiliser sa position native
    }
    
    response = requests.post(
        f"{BASE_URL}/teams/{team_id}/roster",
        json=add_data,
        headers=headers
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ {result['message']}")
        print(f"   💰 Nouveau salary cap : ${result['salary_cap_used']/1_000_000:.1f}M")
        print(f"   💵 Budget restant : ${result['salary_cap_remaining']/1_000_000:.1f}M")
        print(f"   🔄 Transferts restants : {result['transfers_remaining_this_week']}/2")
    else:
        print(f"❌ Erreur : {response.status_code}")
        print(response.json())
else:
    print("⚠️  Aucun joueur abordable trouvé")

# ========================================
# 7. AFFICHER LE ROSTER MIS À JOUR
# ========================================
print("\n" + "=" * 80)
print("👥 ÉTAPE 7 : Roster après ajout")
print("=" * 80)

response = requests.get(f"{BASE_URL}/teams/{team_id}/roster", headers=headers)
if response.status_code == 200:
    roster = response.json()
    print(f"✅ Roster de '{roster['team_name']}' :")
    print(f"   💰 Salary cap utilisé : ${roster['salary_cap_used']/1_000_000:.1f}M / $60M")
    print(f"   💵 Budget restant : ${roster['salary_cap_remaining']/1_000_000:.1f}M")
    print(f"\n   Positions :")
    for slot in roster['roster']:
        if slot['player']:
            print(f"      {slot['position_slot']} : {slot['player']['full_name']} (${slot['acquired_salary']/1_000_000:.1f}M)")
        else:
            print(f"      {slot['position_slot']} : [LIBRE]")
else:
    print(f"❌ Erreur : {response.status_code}")
    print(response.json())

print("\n" + "=" * 80)
print("✅ TEST TERMINÉ !")
print("=" * 80)

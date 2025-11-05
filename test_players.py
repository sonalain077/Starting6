"""
Script de test pour les endpoints Players

Tests :
1. Lister les joueurs (GET /players)
2. Filtrer par position (GET /players?position=PG)
3. Filtrer par salaire (GET /players?min_salary=X&max_salary=Y)
4. Rechercher par nom (GET /players?search=LeBron)
5. Obtenir un joueur spécifique (GET /players/{id})
6. Tester pagination (skip/limit)
7. Tester tri (sort_by/sort_order)
"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000/api/v1"

def print_separator(title: str):
    """Affiche un séparateur visuel"""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def print_response(response: requests.Response):
    """Affiche la réponse de manière formatée"""
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Erreur : {response.text}")

# ========================================
# Test 1 : Lister tous les joueurs (pagination par défaut)
# ========================================
print_separator("Test 1 : Liste des joueurs (défaut)")
response = requests.get(f"{BASE_URL}/players")
print_response(response)

if response.status_code == 200:
    data = response.json()
    print(f"\n📊 Total joueurs : {data['total']}")
    print(f"📄 Joueurs retournés : {len(data['players'])}")
    print(f"🎯 Filtres appliqués : {data['filters_applied']}")
    
    if data['players']:
        print(f"\n🏀 Premier joueur :")
        player = data['players'][0]
        print(f"   - Nom : {player['first_name']} {player['last_name']}")
        print(f"   - Poste : {player['position']}")
        print(f"   - Équipe : {player['team']}")
        print(f"   - Salaire : ${player['fantasy_cost']:,.0f}")

# ========================================
# Test 2 : Filtrer par position (PG)
# ========================================
print_separator("Test 2 : Filtrer les meneurs (PG)")
response = requests.get(f"{BASE_URL}/players", params={"position": "PG", "limit": 5})
print_response(response)

if response.status_code == 200:
    data = response.json()
    print(f"\n🎯 Meneurs trouvés : {data['total']}")
    for p in data['players']:
        print(f"   - {p['first_name']} {p['last_name']} ({p['team']})")

# ========================================
# Test 3 : Filtrer par salaire (5M$ - 10M$)
# ========================================
print_separator("Test 3 : Joueurs entre 5M$ et 10M$")
response = requests.get(
    f"{BASE_URL}/players",
    params={
        "min_salary": 5_000_000,
        "max_salary": 10_000_000,
        "limit": 5,
        "sort_by": "fantasy_cost",
        "sort_order": "desc"
    }
)
print_response(response)

if response.status_code == 200:
    data = response.json()
    print(f"\n💰 Joueurs dans la fourchette : {data['total']}")
    for p in data['players']:
        print(f"   - {p['first_name']} {p['last_name']} : ${p['fantasy_cost']:,.0f}")

# ========================================
# Test 4 : Rechercher par nom
# ========================================
print_separator("Test 4 : Recherche par nom (Curry)")
response = requests.get(f"{BASE_URL}/players", params={"search": "Curry", "limit": 10})
print_response(response)

if response.status_code == 200:
    data = response.json()
    print(f"\n🔍 Résultats pour 'Curry' : {data['total']}")
    for p in data['players']:
        print(f"   - {p['first_name']} {p['last_name']} ({p['position']} - {p['team']})")

# ========================================
# Test 5 : Obtenir un joueur spécifique
# ========================================
print_separator("Test 5 : Détails d'un joueur (ID = 3 - LeBron)")
response = requests.get(f"{BASE_URL}/players/3")
print_response(response)

if response.status_code == 200:
    player = response.json()
    print(f"\n📋 Détails complets :")
    print(f"   - ID : {player['id']}")
    print(f"   - Nom : {player['first_name']} {player['last_name']}")
    print(f"   - Poste : {player['position']}")
    print(f"   - Équipe : {player['team']}")
    print(f"   - Salaire : ${player['fantasy_cost']:,.0f}")
    print(f"   - Moyenne 15 matchs : {player['avg_fantasy_score_last_15']:.1f} pts")
    print(f"   - Matchs joués (20j) : {player['games_played_last_20']}")
    print(f"   - Actif : {'✅' if player['is_active'] else '❌'}")

# ========================================
# Test 6 : Pagination avancée
# ========================================
print_separator("Test 6 : Pagination (skip=10, limit=5)")
response = requests.get(f"{BASE_URL}/players", params={"skip": 10, "limit": 5})
print_response(response)

if response.status_code == 200:
    data = response.json()
    print(f"\n📄 Résultats {data['skip'] + 1} à {data['skip'] + len(data['players'])}")
    print(f"   Total disponible : {data['total']}")

# ========================================
# Test 7 : Tri par performance (avg_fantasy_score_last_15)
# ========================================
print_separator("Test 7 : Top 5 meilleurs performeurs")
response = requests.get(
    f"{BASE_URL}/players",
    params={
        "sort_by": "avg_fantasy_score_last_15",
        "sort_order": "desc",
        "limit": 5
    }
)
print_response(response)

if response.status_code == 200:
    data = response.json()
    print(f"\n🏆 Top 5 des meilleurs performeurs :")
    for i, p in enumerate(data['players'], 1):
        print(f"   {i}. {p['first_name']} {p['last_name']} - {p['avg_fantasy_score_last_15']:.1f} pts")

# ========================================
# Test 8 : Joueur inexistant (404)
# ========================================
print_separator("Test 8 : Joueur inexistant (ID = 99999)")
response = requests.get(f"{BASE_URL}/players/99999")
print_response(response)

if response.status_code == 404:
    print("\n✅ Gestion d'erreur 404 correcte")

# ========================================
# Test 9 : Filtres combinés (position + équipe + salaire)
# ========================================
print_separator("Test 9 : Filtres combinés (PG de LAL > 5M$)")
response = requests.get(
    f"{BASE_URL}/players",
    params={
        "position": "PG",
        "team": "LAL",
        "min_salary": 5_000_000,
        "limit": 10
    }
)
print_response(response)

if response.status_code == 200:
    data = response.json()
    print(f"\n🎯 Filtres appliqués : {json.dumps(data['filters_applied'], indent=2)}")
    print(f"📊 Résultats : {len(data['players'])} joueurs")

print("\n" + "=" * 60)
print("✅ Tests terminés !")
print("=" * 60)

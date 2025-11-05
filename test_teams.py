"""
Test des endpoints FantasyTeam
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("🧪 Test des Endpoints FantasyTeam\n")
print("=" * 60)

# 0. Créer un utilisateur de test (ou se connecter)
username = "test_fantasy"
password = "TestPass123"

print("\n0️⃣ Création/Connexion utilisateur de test...")
response = requests.post(
    f"{BASE_URL}/auth/inscription",
    json={"nom_utilisateur": username, "mot_de_passe": password}
)
if response.status_code == 201:
    print(f"✅ Utilisateur créé: {username}")
elif response.status_code == 400:
    print(f"⚠️  Utilisateur existe déjà, connexion...")

# 1. Se connecter
print("\n1️⃣ Connexion...")
response = requests.post(
    f"{BASE_URL}/auth/connexion",
    json={"nom_utilisateur": username, "mot_de_passe": password}
)

if response.status_code != 200:
    print(f"❌ Connexion échouée: {response.json()}")
    exit(1)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ Token obtenu")

# 2. Créer une équipe dans la ligue SOLO
print("\n2️⃣ Créer une équipe dans la ligue SOLO (ID=1)...")
response = requests.post(
    f"{BASE_URL}/teams",
    json={
        "name": "Les Mavericks de Paris",
        "league_id": 1  # Ligue SOLO
    },
    headers=headers
)

print(f"Status: {response.status_code}")
if response.status_code == 201:
    team = response.json()
    team_id = team["id"]
    print(f"✅ Équipe créée: {team['name']} (ID: {team_id})")
    print(f"   Salary cap utilisé: {team['salary_cap_used']}$")
    print(f"   Waiver priority: {team['waiver_priority']}")
elif response.status_code == 400:
    print(f"⚠️  {response.json()['detail']}")
    # Récupérer l'équipe existante
    response = requests.get(f"{BASE_URL}/teams/me", headers=headers)
    if response.json():
        team_id = response.json()[0]["id"]
        print(f"   Utilisation de l'équipe existante (ID: {team_id})")
else:
    print(f"❌ Erreur: {response.json()}")
    exit(1)

# 3. Lister mes équipes
print("\n3️⃣ Lister mes équipes...")
response = requests.get(f"{BASE_URL}/teams/me", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    teams = response.json()
    print(f"✅ {len(teams)} équipe(s) trouvée(s):")
    for team in teams:
        print(f"   - {team['name']} dans {team['league_name']} ({team['league_type']})")

# 4. Récupérer les détails de l'équipe (public)
print(f"\n4️⃣ Récupérer les détails de l'équipe {team_id} (sans auth)...")
response = requests.get(f"{BASE_URL}/teams/{team_id}")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    team = response.json()
    print(f"✅ Équipe: {team['name']}")
    print(f"   Owner ID: {team['owner_id']}")
    print(f"   League ID: {team['league_id']}")

# 5. Modifier le nom de l'équipe
print(f"\n5️⃣ Modifier le nom de l'équipe...")
response = requests.patch(
    f"{BASE_URL}/teams/{team_id}",
    json={"name": "Les Mavericks de Paname 🔥"},
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    team = response.json()
    print(f"✅ Nom modifié: {team['name']}")

# 6. Essayer de créer une 2ème équipe dans la même ligue (doit échouer)
print("\n6️⃣ Essayer de créer une 2ème équipe dans SOLO (doit échouer)...")
response = requests.post(
    f"{BASE_URL}/teams",
    json={
        "name": "Mon autre équipe",
        "league_id": 1
    },
    headers=headers
)
print(f"Status: {response.status_code}")
if response.status_code == 400:
    print(f"✅ Erreur attendue: {response.json()['detail']}")
else:
    print(f"❌ Devrait retourner 400!")

print("\n" + "=" * 60)
print("🎉 Tests terminés!")

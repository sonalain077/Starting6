"""
Test complet du flow d'authentification
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

print("🧪 Test Complet d'Authentification\n")
print("=" * 50)

# Vérifier que le serveur est accessible
print("\n⏳ Vérification que le serveur est démarré...")
max_retries = 5
for i in range(max_retries):
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=2)
        if response.status_code == 200:
            print("✅ Serveur accessible!")
            break
    except requests.exceptions.RequestException:
        if i < max_retries - 1:
            print(f"   Tentative {i+1}/{max_retries}... Réessai dans 2s")
            time.sleep(2)
        else:
            print("❌ ERREUR: Le serveur n'est pas accessible!")
            print("   Lance d'abord: cd backend && python -m uvicorn app.main:app --reload --port 8000")
            exit(1)

# 1. Test de connexion avec les vrais identifiants
print("\n1️⃣ Connexion avec sonalain03...")
response = requests.post(
    f"{BASE_URL}/auth/connexion",
    json={
        "nom_utilisateur": "sonalain03",
        "mot_de_passe": "Tennis@2003"  # Remplace par ton vrai mot de passe
    }
)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    token = data.get("access_token")
    print(f"✅ Token reçu: {token[:30]}...")
    
    # 2. Test de récupération de la ligue SOLO (public, pas besoin de token)
    print("\n2️⃣ Test GET /leagues/solo (public)...")
    response2 = requests.get(f"{BASE_URL}/leagues/solo")
    print(f"Status: {response2.status_code}")
    if response2.status_code == 200:
        print(f"✅ Ligue SOLO: {response2.json()['name']}")
    
    # 3. Test de création de ligue (nécessite token)
    print("\n3️⃣ Test POST /leagues (authentifié)...")
    response3 = requests.post(
        f"{BASE_URL}/leagues",
        json={
            "name": "Ma Ligue Test",
            "max_teams": 10
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status: {response3.status_code}")
    if response3.status_code == 201:
        print(f"✅ Ligue créée: {response3.json()['name']}")
    else:
        print(f"❌ Erreur: {response3.json()}")
    
    # 4. Test de liste des ligues
    print("\n4️⃣ Test GET /leagues (liste)...")
    response4 = requests.get(f"{BASE_URL}/leagues")
    print(f"Status: {response4.status_code}")
    if response4.status_code == 200:
        data = response4.json()
        print(f"✅ {data['total']} ligues trouvées")
        for league in data['leagues']:
            print(f"   - {league['name']} ({league['type']})")

else:
    print(f"❌ Erreur de connexion: {response.status_code}")
    print(response.json())

print("\n" + "=" * 50)
print("🎉 Tests terminés!")

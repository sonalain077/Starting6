"""
Script de test pour débugger l'authentification
"""
import requests

# URL de base
BASE_URL = "http://127.0.0.1:8000/api/v1"

# 1. Test de connexion
print("🔐 Test de connexion...")
response = requests.post(
    f"{BASE_URL}/auth/connexion",
    json={
        "nom_utilisateur": "sonalain03",  # ← EN MINUSCULES !
        "mot_de_passe": "ton_mot_de_passe_ici"  # ← Mets ton vrai mot de passe
    }
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    token = data.get("access_token")
    print(f"\n✅ Token reçu: {token[:50]}...")
    
    # 2. Test du token avec un endpoint protégé
    print("\n🔒 Test du token avec GET /leagues/solo...")
    response2 = requests.get(
        f"{BASE_URL}/leagues/solo",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(f"Status Code: {response2.status_code}")
    print(f"Response: {response2.json()}")
else:
    print(f"\n❌ Erreur de connexion!")
    print(f"Détails: {response.json()}")

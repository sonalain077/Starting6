"""
Script de test pour l'endpoint /leagues/solo
"""
import requests
import json

print("🧪 Test de l'endpoint GET /api/v1/leagues/solo\n")

try:
    response = requests.get("http://127.0.0.1:8000/api/v1/leagues/solo")
    
    print(f"📊 Status Code: {response.status_code}")
    print(f"📄 Response Headers: {dict(response.headers)}\n")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS! Ligue SOLO récupérée:\n")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ ERREUR {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ ERREUR: Impossible de se connecter au serveur")
    print("Vérifiez que FastAPI tourne sur http://127.0.0.1:8000")
except Exception as e:
    print(f"❌ ERREUR inattendue: {e}")

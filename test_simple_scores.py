"""
Test simple pour voir l'erreur exacte
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

print("🧪 Test endpoint leaderboard SOLO...")
try:
    response = requests.get(f"{BASE_URL}/leagues/solo/leaderboard")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Succès: {response.json()}")
    else:
        print(f"❌ Erreur: {response.text}")
except Exception as e:
    print(f"❌ Exception: {e}")

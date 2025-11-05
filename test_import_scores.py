"""Test d'import direct pour voir l'erreur"""
import sys
sys.path.insert(0, r'C:\Users\phams\Desktop\ProjetFullstack\backend')

try:
    from app.api.v1.endpoints import scores
    print("✅ Import scores OK")
    
    # Tester d'appeler une fonction
    from app.core.database import SessionLocal
    db = SessionLocal()
    
    from app.models.league import League
    league = db.query(League).filter(League.id == 1).first()
    
    if league:
        print(f"✅ Ligue trouvée: {league.name}")
        print(f"   Type: {league.type}")
        print(f"   start_date: {league.start_date}")
        print(f"   Type de start_date: {type(league.start_date)}")
    else:
        print("❌ Ligue SOLO introuvable")
    
    db.close()
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

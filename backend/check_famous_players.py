from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.player import Player
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Joueurs célèbres pour vérifier les positions
test_names = [
    "Stephen Curry",  # Devrait être PG
    "LeBron James",   # Devrait être SF
    "Nikola Jokic",   # Devrait être C
    "Giannis",        # Devrait être PF
    "Luka Doncic",    # Devrait être PG
    "Damian Lillard", # Devrait être PG
    "Kevin Durant",   # Devrait être SF/PF
    "Joel Embiid",    # Devrait être C
]

print("\n🔍 Vérification des positions de joueurs célèbres:")
print("=" * 60)

for name in test_names:
    players = db.query(Player).filter(Player.full_name.ilike(f"%{name}%")).all()
    if players:
        for p in players:
            print(f"  {p.full_name:25s} → {p.position.name:3s} ({p.team})")
    else:
        print(f"  {name:25s} → NON TROUVÉ")

print("=" * 60)

db.close()

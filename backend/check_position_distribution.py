from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models.player import Player
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

positions = db.query(Player.position, func.count(Player.id)).group_by(Player.position).all()

print("\n📊 Distribution des postes:")
print("=" * 40)
total = 0
for pos, count in sorted(positions, key=lambda x: x[1], reverse=True):
    print(f"  {pos.name:3s}: {count:3d} joueurs")
    total += count

print("=" * 40)
print(f"Total: {total} joueurs\n")

db.close()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.player import Player, Position
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("\n🏀 Top 5 Point Guards disponibles:")
print("=" * 80)

pgs = db.query(Player).filter(Player.position == Position.PG).order_by(Player.full_name).limit(10).all()

for pg in pgs:
    print(f"  {pg.full_name:25s} | {pg.team:4s} | ${pg.fantasy_cost/1_000_000:.1f}M")

print("=" * 80)
print(f"\nTotal PG disponibles: {db.query(Player).filter(Player.position == Position.PG).count()}")

db.close()

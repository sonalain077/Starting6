"""
Script de diagnostic pour vérifier la base de données des joueurs NBA
"""

import sys
sys.path.append('backend')

from app.core.database import SessionLocal
from app.models.player import Player
from sqlalchemy import func

db = SessionLocal()

print("=" * 60)
print("DIAGNOSTIC BASE DE DONNÉES NBA")
print("=" * 60)

# Total de joueurs
total = db.query(Player).count()
print(f"\n📊 Total de joueurs dans la DB: {total}")

# Distribution par position
print("\n📍 Distribution par position:")
positions = db.query(
    Player.position, 
    func.count(Player.id).label('count')
).group_by(Player.position).all()

for pos, count in sorted(positions, key=lambda x: x[0].value):
    print(f"   {pos.value}: {count} joueurs")

# Joueurs actifs vs inactifs
actifs = db.query(Player).filter(Player.is_active == True).count()
inactifs = db.query(Player).filter(Player.is_active == False).count()
print(f"\n✅ Joueurs actifs: {actifs}")
print(f"❌ Joueurs inactifs: {inactifs}")

# Échantillon de joueurs récents (basé sur l'ID)
print("\n🏀 Derniers joueurs ajoutés (par ID):")
recent = db.query(Player).order_by(Player.id.desc()).limit(10).all()
for p in recent:
    status = "✅" if p.is_active else "❌"
    print(f"   {status} {p.first_name} {p.last_name} - {p.position.value} ({p.team}) - ${p.fantasy_cost/1_000_000:.1f}M")

# Rechercher des rookies 2024-2025 (par nom connu)
print("\n👶 Recherche de rookies de la draft 2024:")
rookies_2024 = [
    "Zaccharie Risacher",  # 1st pick
    "Alexandre Sarr",      # 2nd pick
    "Reed Sheppard",       # 3rd pick
    "Stephon Castle",      # 4th pick
    "Ron Holland",         # 5th pick
    "Matas Buzelis",
    "Donovan Clingan",
    "Rob Dillingham",
    "Zach Edey",
    "Cody Williams"
]

for rookie_name in rookies_2024:
    parts = rookie_name.split()
    first_name = parts[0]
    last_name = " ".join(parts[1:])
    
    player = db.query(Player).filter(
        func.lower(Player.first_name).like(f"%{first_name.lower()}%"),
        func.lower(Player.last_name).like(f"%{last_name.lower()}%")
    ).first()
    
    if player:
        print(f"   ✅ Trouvé: {player.first_name} {player.last_name} ({player.team})")
    else:
        print(f"   ❌ MANQUANT: {rookie_name}")

# Vérifier les équipes représentées
print("\n🏟️  Équipes NBA représentées:")
teams = db.query(Player.team, func.count(Player.id).label('count')).group_by(Player.team).order_by(func.count(Player.id).desc()).all()
print(f"   Total: {len(teams)} équipes")
for team, count in teams[:10]:
    print(f"   {team}: {count} joueurs")

db.close()
print("\n" + "=" * 60)

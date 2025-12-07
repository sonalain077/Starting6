"""
Script pour calculer les salaires fantasy dynamiques des joueurs NBA

Formule :
- Base : (avg_fantasy_score_last_15 / 5) * 1_000_000
- Min : 2M$ (rookies/bench)
- Max : 18M$ (superstars)

Pour l'instant, on génère des salaires simulés basés sur le poste et le nom
car on n'a pas encore de scores fantasy calculés.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.player import Player, Position
from app.core.config import settings
import random

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Joueurs stars connus (salaire élevé)
SUPERSTAR_NAMES = [
    "Stephen Curry", "LeBron James", "Kevin Durant", "Giannis Antetokounmpo",
    "Joel Embiid", "Nikola Jokić", "Luka Dončić", "Jayson Tatum",
    "Damian Lillard", "Anthony Davis", "James Harden", "Kawhi Leonard",
    "Devin Booker", "Ja Morant", "Trae Young", "Donovan Mitchell"
]

# Joueurs All-Stars (salaire moyen-élevé)
ALLSTAR_NAMES = [
    "Tyrese Maxey", "Paolo Banchero", "Franz Wagner", "Desmond Bane",
    "Cade Cunningham", "Jalen Green", "Scottie Barnes", "Evan Mobley",
    "Anthony Edwards", "Shai Gilgeous-Alexander", "De'Aaron Fox"
]

def calculate_salary_tier(player: Player) -> float:
    """
    Calcule le salaire en fonction du niveau du joueur
    """
    full_name = player.full_name
    
    # Superstars : 12M$ - 18M$
    if any(name in full_name for name in SUPERSTAR_NAMES):
        return random.uniform(12_000_000, 18_000_000)
    
    # All-Stars : 8M$ - 12M$
    if any(name in full_name for name in ALLSTAR_NAMES):
        return random.uniform(8_000_000, 12_000_000)
    
    # Titulaires par position
    if player.position == Position.PG:
        return random.uniform(4_000_000, 9_000_000)  # PG valuable
    elif player.position == Position.C:
        return random.uniform(4_500_000, 9_500_000)  # Centers valuable
    elif player.position == Position.SG:
        return random.uniform(3_500_000, 8_000_000)
    elif player.position == Position.SF:
        return random.uniform(3_500_000, 8_000_000)
    elif player.position == Position.PF:
        return random.uniform(4_000_000, 8_500_000)
    
    # Défaut
    return random.uniform(2_500_000, 6_000_000)


def update_all_salaries():
    """
    Met à jour les salaires de tous les joueurs
    """
    print("\n" + "=" * 80)
    print("💰 CALCUL DES SALAIRES FANTASY DYNAMIQUES")
    print("=" * 80)
    
    players = db.query(Player).all()
    print(f"\n📊 {len(players)} joueurs à traiter...\n")
    
    updates = {
        "superstars": 0,
        "allstars": 0,
        "starters": 0,
        "bench": 0
    }
    
    for i, player in enumerate(players, 1):
        old_salary = player.fantasy_cost
        new_salary = calculate_salary_tier(player)
        
        player.fantasy_cost = round(new_salary, 2)
        
        # Catégoriser
        if new_salary >= 12_000_000:
            updates["superstars"] += 1
            tier = "⭐ SUPERSTAR"
        elif new_salary >= 8_000_000:
            updates["allstars"] += 1
            tier = "🌟 ALL-STAR"
        elif new_salary >= 5_000_000:
            updates["starters"] += 1
            tier = "✅ STARTER"
        else:
            updates["bench"] += 1
            tier = "📋 BENCH"
        
        if i % 50 == 0:
            print(f"  Progression : {i}/{len(players)} joueurs traités...")
        
        # Afficher quelques exemples
        if new_salary >= 12_000_000 or any(name in player.full_name for name in SUPERSTAR_NAMES[:5]):
            print(f"  {tier} | {player.full_name:30s} → ${new_salary/1_000_000:.1f}M ({player.position.value})")
    
    db.commit()
    
    print("\n" + "=" * 80)
    print("✅ MISE À JOUR TERMINÉE")
    print("=" * 80)
    print(f"\n📊 Répartition des salaires :")
    print(f"  ⭐ Superstars (12M$+)  : {updates['superstars']} joueurs")
    print(f"  🌟 All-Stars (8-12M$)  : {updates['allstars']} joueurs")
    print(f"  ✅ Starters (5-8M$)    : {updates['starters']} joueurs")
    print(f"  📋 Bench (2-5M$)       : {updates['bench']} joueurs")
    print(f"\n  💰 Total : {len(players)} joueurs")
    
    # Statistiques
    avg_salary = sum(p.fantasy_cost for p in players) / len(players)
    min_salary = min(p.fantasy_cost for p in players)
    max_salary = max(p.fantasy_cost for p in players)
    
    print(f"\n📈 Stats globales :")
    print(f"  • Salaire moyen   : ${avg_salary/1_000_000:.2f}M")
    print(f"  • Salaire min     : ${min_salary/1_000_000:.2f}M")
    print(f"  • Salaire max     : ${max_salary/1_000_000:.2f}M")
    print("=" * 80 + "\n")
    
    db.close()


if __name__ == "__main__":
    update_all_salaries()

#!/usr/bin/env python3
"""Check salaries for team 'clip'"""

import sys
sys.path.append('backend')

from app.core.database import SessionLocal
from app.models.player import Player
from app.models.fantasy_team_player import FantasyTeamPlayer

db = SessionLocal()

print("\n🏀 ROSTER CLIP - NOUVEAUX SALAIRES\n")
print(f"{'Poste':<6} {'Joueur':<30} {'Salaire':>12}")
print("-" * 50)

roster = db.query(FantasyTeamPlayer).filter(
    FantasyTeamPlayer.fantasy_team_id == 5
).all()

total = 0
for slot in roster:
    player = db.query(Player).filter(Player.id == slot.player_id).first()
    salary_m = player.fantasy_cost / 1_000_000
    total += player.fantasy_cost
    print(f"{slot.position_slot:<6} {player.full_name:<30} ${salary_m:>10.2f}M")

total_m = total / 1_000_000
pct = (total_m / 60) * 100

print("-" * 50)
print(f"{'TOTAL':<6} {'':<30} ${total_m:>10.2f}M")
print(f"\n💰 Budget utilisé: {total_m:.2f}M / 60M ({pct:.1f}%)")
print(f"💵 Budget restant: {60 - total_m:.2f}M\n")

db.close()

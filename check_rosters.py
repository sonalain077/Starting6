"""
Script pour vérifier l'état des rosters et les compléter
"""
import sys
sys.path.insert(0, 'backend')

from app.core.database import SessionLocal
from app.models.fantasy_team import FantasyTeam
from app.models.fantasy_team_player import FantasyTeamPlayer
from app.models.player import Player

db = SessionLocal()

print("=" * 80)
print("📊 ÉTAT DES ROSTERS")
print("=" * 80)

teams = db.query(FantasyTeam).all()

for team in teams:
    print(f"\n🏀 {team.name} (ID {team.id})")
    print(f"   Ligue: {team.league.name}")
    print(f"   Salary cap utilisé: ${team.salary_cap_used:,.0f}")
    
    players = db.query(FantasyTeamPlayer).filter(
        FantasyTeamPlayer.fantasy_team_id == team.id
    ).all()
    
    print(f"   Roster ({len(players)}/6 joueurs):")
    
    slots_filled = {}
    for p in players:
        print(f"      {p.roster_slot}: {p.player.full_name} ({p.player.team}) - ${p.salary_at_acquisition:,.0f}")
        slots_filled[p.roster_slot] = True
    
    # Afficher les slots vides
    required_slots = ['PG', 'SG', 'SF', 'PF', 'C', 'UTIL']
    empty_slots = [slot for slot in required_slots if slot not in slots_filled]
    
    if empty_slots:
        print(f"   ⚠️  Slots vides: {', '.join(empty_slots)}")
    else:
        print(f"   ✅ Roster complet!")

db.close()

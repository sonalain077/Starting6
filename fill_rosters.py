"""
Script pour compléter les rosters des équipes
"""
import sys
sys.path.insert(0, 'backend')

from app.core.database import SessionLocal
from app.models.fantasy_team import FantasyTeam
from app.models.fantasy_team_player import FantasyTeamPlayer
from app.models.player import Player
from datetime import datetime

db = SessionLocal()

print("=" * 80)
print("🔧 COMPLÉTION DES ROSTERS")
print("=" * 80)

# Équipe 2 : Test Roster Team - Il manque le PG
print("\n🏀 Équipe 2: Test Roster Team")

team = db.query(FantasyTeam).filter(FantasyTeam.id == 2).first()
current_players = db.query(FantasyTeamPlayer).filter(
    FantasyTeamPlayer.fantasy_team_id == 2
).all()

print(f"   Joueurs actuels: {len(current_players)}/6")
for p in current_players:
    print(f"      {p.roster_slot}: {p.player.full_name}")

# Vérifier les slots occupés
occupied_slots = [p.roster_slot for p in current_players]
print(f"\n   Slots occupés: {occupied_slots}")

# Il manque PG
# Cherchons un bon PG pas trop cher
available_pgs = db.query(Player).filter(
    Player.position == 'PG',
    Player.fantasy_cost <= (60_000_000 - team.salary_cap_used)  # Budget restant
).order_by(Player.fantasy_cost.desc()).limit(10).all()

print(f"\n   💰 Budget restant: ${60_000_000 - team.salary_cap_used:,.0f}")
print(f"\n   🔍 Meilleurs PG disponibles dans le budget:")
for pg in available_pgs[:5]:
    print(f"      - {pg.full_name} ({pg.team}) - ${pg.fantasy_cost:,.0f}")

# Ajoutons Luka Doncic si disponible, sinon le premier de la liste
luka = db.query(Player).filter(
    Player.full_name.like('%Doncic%')
).first()

if luka and luka.fantasy_cost <= (60_000_000 - team.salary_cap_used):
    selected_pg = luka
    print(f"\n   ✅ Sélection: {selected_pg.full_name}")
else:
    selected_pg = available_pgs[0] if available_pgs else None
    if selected_pg:
        print(f"\n   ✅ Sélection: {selected_pg.full_name}")
    else:
        print("\n   ❌ Aucun PG disponible dans le budget!")

if selected_pg:
    # Ajouter le joueur
    new_player = FantasyTeamPlayer(
        fantasy_team_id=2,
        player_id=selected_pg.id,
        roster_slot='PG',
        salary_at_acquisition=selected_pg.fantasy_cost,
        date_acquired=datetime.now()
    )
    db.add(new_player)
    
    # Mettre à jour le salary cap
    team.salary_cap_used += selected_pg.fantasy_cost
    team.is_roster_complete = 1
    
    db.commit()
    
    print(f"\n   ✅ {selected_pg.full_name} ajouté au poste PG!")
    print(f"   💰 Nouveau salary cap: ${team.salary_cap_used:,.0f} / $60,000,000")
    print(f"   ✅ Roster complet: 6/6 joueurs")

# Équipe 1 : Les Mavericks de Paname - Complètement vide
print("\n" + "=" * 80)
print("🏀 Équipe 1: Les Mavericks de Paname 🔥")
print("   Cette équipe est vide. Création d'un roster complet...")

team1 = db.query(FantasyTeam).filter(FantasyTeam.id == 1).first()

# Sélection de joueurs pour chaque poste (budget $60M)
roster_to_create = {
    'PG': None,  # ~$10M
    'SG': None,  # ~$10M
    'SF': None,  # ~$10M
    'PF': None,  # ~$10M
    'C': None,   # ~$10M
    'UTIL': None # ~$10M
}

budget_per_position = 10_000_000

for position in ['PG', 'SG', 'SF', 'PF', 'C']:
    # Trouver un bon joueur pour ce poste
    players = db.query(Player).filter(
        Player.position == position,
        Player.fantasy_cost <= budget_per_position * 1.2  # 20% de flexibilité
    ).order_by(Player.fantasy_cost.desc()).limit(1).all()
    
    if players:
        selected = players[0]
        roster_to_create[position] = selected
        print(f"   {position}: {selected.full_name} ({selected.team}) - ${selected.fantasy_cost:,.0f}")

# UTIL - prendre n'importe quel poste
util_players = db.query(Player).filter(
    Player.fantasy_cost <= budget_per_position * 1.2
).order_by(Player.fantasy_cost.desc()).limit(1).all()

if util_players:
    roster_to_create['UTIL'] = util_players[0]
    print(f"   UTIL: {util_players[0].full_name} ({util_players[0].team}) - ${util_players[0].fantasy_cost:,.0f}")

# Vérifier le budget total
total_salary = sum(p.fantasy_cost for p in roster_to_create.values() if p)
print(f"\n   💰 Coût total: ${total_salary:,.0f} / $60,000,000")

if total_salary <= 60_000_000:
    print(f"   ✅ Budget OK! Ajout des joueurs...")
    
    for slot, player in roster_to_create.items():
        if player:
            new_player = FantasyTeamPlayer(
                fantasy_team_id=1,
                player_id=player.id,
                roster_slot=slot,
                salary_at_acquisition=player.fantasy_cost,
                date_acquired=datetime.now()
            )
            db.add(new_player)
    
    team1.salary_cap_used = total_salary
    team1.is_roster_complete = 1
    
    db.commit()
    
    print(f"   ✅ Roster complet créé!")
else:
    print(f"   ❌ Budget dépassé!")

print("\n" + "=" * 80)
print("✅ COMPLÉTION TERMINÉE")
print("=" * 80)

db.close()

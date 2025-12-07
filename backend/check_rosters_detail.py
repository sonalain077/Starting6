from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.fantasy_team import FantasyTeam
from app.models.fantasy_team_player import FantasyTeamPlayer
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

teams = db.query(FantasyTeam).all()

print('\n' + '=' * 80)
print('🏀 ANALYSE DES ROSTERS'.center(80))
print('=' * 80)

for team in teams:
    roster = db.query(FantasyTeamPlayer).filter(
        FantasyTeamPlayer.fantasy_team_id == team.id
    ).all()
    
    print(f'\n📋 {team.name} (Owner: {team.owner.nom_utilisateur})')
    print(f'   Joueurs: {len(roster)}/6')
    print('   ' + '-' * 76)
    
    if len(roster) > 0:
        for slot in roster:
            print(f'   {slot.roster_slot.value:4s} → {slot.player.full_name:25s} ({slot.player.team})')
    else:
        print('   ❌ Aucun joueur dans le roster')
    
    # Calculer le budget utilisé
    total_cost = sum([slot.player.fantasy_cost for slot in roster])
    budget_pct = (total_cost / 60_000_000) * 100
    print(f'   Budget: ${total_cost/1_000_000:.1f}M / 60M ({budget_pct:.1f}%)')

print('\n' + '=' * 80)
db.close()

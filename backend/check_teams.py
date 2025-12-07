from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.fantasy_team import FantasyTeam
from app.models.utilisateur import Utilisateur
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

users = db.query(Utilisateur).all()
print('\n🔍 Utilisateurs dans la base:')
print('=' * 50)
for u in users:
    print(f'  - {u.nom_utilisateur} (ID: {u.id})')

teams = db.query(FantasyTeam).all()
print(f'\n🏀 Équipes créées: {len(teams)}')
print('=' * 50)
for t in teams:
    league_name = t.league.name if t.league else "None"
    print(f'  - {t.name} (Owner: {t.owner.nom_utilisateur}, League: {league_name})')

db.close()

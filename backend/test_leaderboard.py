from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models.fantasy_team import FantasyTeam
from app.models.fantasy_team_score import FantasyTeamScore
from app.models.utilisateur import Utilisateur
from app.models.league import League, LeagueType
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

# Trouver la ligue SOLO
solo_league = db.query(League).filter(League.type == LeagueType.SOLO).first()

if solo_league:
    print(f"✅ Solo League trouvée: {solo_league.name} (ID: {solo_league.id})")
    
    # Tester la requête
    try:
        teams = db.query(
            FantasyTeam.id,
            FantasyTeam.name,
            Utilisateur.nom_utilisateur.label("username"),
            func.coalesce(func.sum(FantasyTeamScore.total_score), 0).label("total_score"),
            func.count(FantasyTeamScore.id).label("games_played")
        ).join(
            Utilisateur, FantasyTeam.owner_id == Utilisateur.id
        ).outerjoin(
            FantasyTeamScore, FantasyTeam.id == FantasyTeamScore.team_id
        ).filter(
            FantasyTeam.league_id == solo_league.id
        ).group_by(
            FantasyTeam.id, FantasyTeam.name, Utilisateur.nom_utilisateur
        ).order_by(
            func.sum(FantasyTeamScore.total_score).desc()
        ).all()
        
        print(f"\n📋 {len(teams)} équipes trouvées:")
        for team in teams:
            print(f"  - {team.name} (Owner: {team.username}, Score: {team.total_score}, Games: {team.games_played})")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Solo League non trouvée")

db.close()

"""
Tâche : Mise à jour des classements (leaderboards)
Exécution : Tous les jours à 13h30

Recalcule le classement de toutes les ligues (SOLO et PRIVATE)
selon les scores cumulés des équipes
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import SessionLocal
from app.models.league import League, LeagueType
from app.models.fantasy_team import FantasyTeam
from app.models.fantasy_team_score import FantasyTeamScore

logger = logging.getLogger(__name__)


def update_leaderboards():
    """
    Met à jour le classement de toutes les ligues
    
    Pour chaque ligue :
    1. SOLO : Cumul des scores des 7 derniers jours
    2. PRIVATE : Cumul depuis la création de la ligue (season_start)
    
    Calcule :
    - Score total
    - Nombre de matchs comptés
    - Moyenne par jour
    - Classement (rank)
    
    Note : Le classement est recalculé à chaque fois
    """
    logger.info("=" * 80)
    logger.info("📊 MISE À JOUR DES CLASSEMENTS - DÉBUT")
    logger.info("=" * 80)
    
    db: Session = SessionLocal()
    leagues_processed = 0
    
    try:
        # Récupérer toutes les ligues actives
        all_leagues = db.query(League).filter(League.is_active == True).all()
        
        logger.info(f"🏆 {len(all_leagues)} ligues à traiter")
        
        for league in all_leagues:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"🏆 {league.name} ({league.type.value})")
            logger.info(f"{'=' * 60}")
            
            try:
                # Déterminer la période de calcul
                if league.type == LeagueType.SOLO:
                    # SOLO : 7 derniers jours (rolling week)
                    start_date = datetime.now().date() - timedelta(days=7)
                    logger.info(f"   📅 Période : 7 derniers jours (depuis {start_date})")
                else:
                    # PRIVATE : Depuis le début de la saison
                    start_date = league.start_date or datetime.now().date() - timedelta(days=30)
                    logger.info(f"   📅 Période : Depuis {start_date} (season start)")
                
                # Récupérer toutes les équipes de la ligue
                teams = db.query(FantasyTeam).filter(
                    FantasyTeam.league_id == league.id
                ).all()
                
                logger.info(f"   👥 {len(teams)} équipes dans la ligue")
                
                # Calculer le score de chaque équipe
                team_rankings = []
                
                for team in teams:
                    # Somme des scores depuis start_date
                    total_score = db.query(func.sum(FantasyTeamScore.total_score)).filter(
                        FantasyTeamScore.fantasy_team_id == team.id,
                        FantasyTeamScore.score_date >= start_date
                    ).scalar() or 0.0
                    
                    # Compter le nombre de jours
                    days_count = db.query(func.count(FantasyTeamScore.id)).filter(
                        FantasyTeamScore.fantasy_team_id == team.id,
                        FantasyTeamScore.score_date >= start_date
                    ).scalar() or 0
                    
                    # Moyenne par jour
                    avg_score = total_score / days_count if days_count > 0 else 0.0
                    
                    team_rankings.append({
                        'team': team,
                        'total_score': total_score,
                        'days_count': days_count,
                        'avg_score': avg_score
                    })
                
                # Trier par score total décroissant
                team_rankings.sort(key=lambda x: x['total_score'], reverse=True)
                
                # Afficher le classement
                logger.info("")
                logger.info("   🏅 CLASSEMENT :")
                logger.info("   " + "-" * 60)
                
                for rank, team_data in enumerate(team_rankings, 1):
                    team = team_data['team']
                    total = team_data['total_score']
                    days = team_data['days_count']
                    avg = team_data['avg_score']
                    
                    # Icône de médaille pour le top 3
                    medal = ""
                    if rank == 1:
                        medal = "🥇"
                    elif rank == 2:
                        medal = "🥈"
                    elif rank == 3:
                        medal = "🥉"
                    
                    logger.info(
                        f"   {medal} #{rank:<2} | {team.name:<25} | "
                        f"{total:>7.1f} pts ({days} jours, moy. {avg:.1f})"
                    )
                
                leagues_processed += 1
                
                # TODO: Sauvegarder le classement dans une table dédiée
                # (LeagueLeaderboard ou cache Redis)
                # Pour l'instant, on log juste le résultat
                
            except Exception as e:
                logger.error(f"   ❌ Erreur pour la ligue {league.name} : {e}")
                continue
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"✅ MISE À JOUR TERMINÉE")
        logger.info(f"   Ligues traitées : {leagues_processed}/{len(all_leagues)}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la mise à jour des classements : {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    # Pour tester la tâche manuellement
    logging.basicConfig(level=logging.INFO)
    update_leaderboards()

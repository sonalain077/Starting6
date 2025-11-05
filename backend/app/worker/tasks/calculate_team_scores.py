"""
Tâche : Calcul des scores d'équipes fantasy
Exécution : Tous les jours à 09h00

Calcule le score total de chaque équipe fantasy en additionnant
les scores de ses 6 joueurs pour la journée précédente
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.fantasy_team import FantasyTeam
from app.models.fantasy_team_player import FantasyTeamPlayer
from app.models.fantasy_team_score import FantasyTeamScore
from app.models.player_game_score import PlayerGameScore

logger = logging.getLogger(__name__)


def calculate_yesterday_team_scores():
    """
    Calcule le score de chaque équipe fantasy pour la veille
    
    Pour chaque équipe :
    1. Récupère les 6 joueurs du roster
    2. Somme leurs scores fantasy de la veille
    3. Enregistre le total dans FantasyTeamScore
    
    Note : Si un joueur n'a pas joué, son score = 0
    """
    logger.info("=" * 80)
    logger.info("🏆 CALCUL DES SCORES D'ÉQUIPES - DÉBUT")
    logger.info("=" * 80)
    
    db: Session = SessionLocal()
    teams_processed = 0
    
    try:
        # Date d'hier
        yesterday = datetime.now() - timedelta(days=1)
        score_date = yesterday.date()
        
        logger.info(f"📅 Date cible : {score_date}")
        
        # Récupérer toutes les équipes actives
        teams = db.query(FantasyTeam).all()
        
        logger.info(f"👥 {len(teams)} équipes à traiter")
        
        for team in teams:
            try:
                # Récupérer les joueurs de l'équipe
                team_players = db.query(FantasyTeamPlayer).filter(
                    FantasyTeamPlayer.fantasy_team_id == team.id
                ).all()
                
                if len(team_players) != 6:
                    logger.warning(f"   ⚠️  {team.name} : roster incomplet ({len(team_players)}/6 joueurs)")
                    continue
                
                # Calculer le score total
                total_score = 0.0
                player_scores = []
                
                for team_player in team_players:
                    # Récupérer le score du joueur pour hier
                    player_game_score = db.query(PlayerGameScore).filter(
                        PlayerGameScore.player_id == team_player.player_id,
                        PlayerGameScore.game_date == score_date
                    ).first()
                    
                    if player_game_score:
                        score = player_game_score.fantasy_score
                        total_score += score
                        player_scores.append({
                            'player': team_player.player.full_name,
                            'score': score
                        })
                    else:
                        # Joueur n'a pas joué (repos ou blessé)
                        player_scores.append({
                            'player': team_player.player.full_name,
                            'score': 0.0
                        })
                
                # Vérifier si le score existe déjà
                existing_score = db.query(FantasyTeamScore).filter(
                    FantasyTeamScore.fantasy_team_id == team.id,
                    FantasyTeamScore.score_date == score_date
                ).first()
                
                if existing_score:
                    # Mettre à jour
                    existing_score.total_score = total_score
                else:
                    # Créer nouveau score
                    team_score = FantasyTeamScore(
                        fantasy_team_id=team.id,
                        score_date=score_date,
                        total_score=total_score
                    )
                    db.add(team_score)
                
                teams_processed += 1
                
                # Logger les détails
                logger.info(f"\n✅ {team.name} : {total_score:.1f} pts")
                for ps in player_scores:
                    if ps['score'] > 0:
                        logger.info(f"   - {ps['player']}: {ps['score']:.1f}")
                    else:
                        logger.info(f"   - {ps['player']}: DNP (repos/blessé)")
                
                # Commit toutes les 20 équipes
                if teams_processed % 20 == 0:
                    db.commit()
                    logger.info(f"\n💾 {teams_processed} équipes traitées...")
                
            except Exception as e:
                logger.error(f"   ❌ Erreur pour l'équipe {team.name} : {e}")
                continue
        
        # Commit final
        db.commit()
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"✅ CALCUL TERMINÉ")
        logger.info(f"   Équipes traitées : {teams_processed}/{len(teams)}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du calcul des scores : {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    # Pour tester la tâche manuellement
    logging.basicConfig(level=logging.INFO)
    calculate_yesterday_team_scores()

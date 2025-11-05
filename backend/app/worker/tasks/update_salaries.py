"""
Tâche : Mise à jour des salaires fantasy
Exécution : Tous les lundis à 10h00

Recalcule le salaire (fantasy_cost) de chaque joueur NBA selon
ses 15 dernières performances + consistance + disponibilité
"""
import logging
import statistics
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import SessionLocal
from app.models.player import Player
from app.models.player_game_score import PlayerGameScore

logger = logging.getLogger(__name__)


def calculate_player_salary(avg_score: float, std_dev: float, games_played: int) -> float:
    """
    Calcule le salaire fantasy d'un joueur selon la formule officielle
    
    Formule :
    1. Salaire de base = (moyenne fantasy / 5) * 1M$
    2. Bonus de consistance = base * (1 - (std_dev / avg)) * 0.15
    3. Facteur de disponibilité = (games_played / 20)
    4. Salaire final = (base + bonus) * disponibilité
    
    Plafonds :
    - Minimum : 2M$
    - Maximum : 18M$
    
    Args:
        avg_score: Moyenne fantasy sur 15 derniers matchs
        std_dev: Écart-type des 15 derniers scores
        games_played: Nombre de matchs joués dans les 20 derniers jours
    
    Returns:
        float: Salaire entre 2M$ et 18M$
    """
    # Salaire de base
    base_salary = (avg_score / 5) * 1_000_000
    
    # Bonus de consistance (joueur régulier = bonus)
    consistency_factor = max(0, 1 - (std_dev / avg_score)) if avg_score > 0 else 0
    consistency_bonus = base_salary * consistency_factor * 0.15
    
    # Facteur de disponibilité (pénalise les blessures)
    availability_factor = games_played / 20
    
    # Salaire final
    final_salary = (base_salary + consistency_bonus) * availability_factor
    
    # Appliquer les plafonds
    return max(2_000_000, min(18_000_000, final_salary))


def update_all_player_salaries():
    """
    Met à jour le salaire de tous les joueurs actifs
    
    Pour chaque joueur :
    1. Récupère les 15 derniers scores fantasy
    2. Calcule moyenne + écart-type
    3. Compte les matchs joués dans les 20 derniers jours
    4. Applique la formule de calcul
    5. Met à jour Player.fantasy_cost
    
    Note : Nécessite au moins 5 matchs pour calculer un salaire
    """
    logger.info("=" * 80)
    logger.info("💰 MISE À JOUR DES SALAIRES - DÉBUT")
    logger.info("=" * 80)
    
    db: Session = SessionLocal()
    players_updated = 0
    players_skipped = 0
    
    try:
        # Date limite : 20 jours avant aujourd'hui
        twenty_days_ago = datetime.now().date() - timedelta(days=20)
        
        logger.info(f"📅 Période d'analyse : {twenty_days_ago} à aujourd'hui")
        
        # Récupérer tous les joueurs actifs
        players = db.query(Player).filter(Player.is_active == True).all()
        
        logger.info(f"👤 {len(players)} joueurs à traiter")
        
        for player in players:
            try:
                # Récupérer les 15 derniers scores
                recent_scores_query = db.query(PlayerGameScore).filter(
                    PlayerGameScore.player_id == player.id,
                    PlayerGameScore.game_date >= twenty_days_ago
                ).order_by(PlayerGameScore.game_date.desc()).limit(15)
                
                recent_scores = [score.fantasy_score for score in recent_scores_query.all()]
                
                # Vérifier s'il y a assez de données
                if len(recent_scores) < 5:
                    players_skipped += 1
                    continue  # Pas assez de matchs pour calculer
                
                # Calculer les statistiques
                avg_score = statistics.mean(recent_scores)
                std_dev = statistics.stdev(recent_scores) if len(recent_scores) > 1 else 0
                
                # Compter les matchs joués dans les 20 derniers jours
                games_count = db.query(func.count(PlayerGameScore.id)).filter(
                    PlayerGameScore.player_id == player.id,
                    PlayerGameScore.game_date >= twenty_days_ago
                ).scalar()
                
                # Calculer le nouveau salaire
                old_salary = player.fantasy_cost
                new_salary = calculate_player_salary(avg_score, std_dev, games_count)
                
                # Mettre à jour
                player.fantasy_cost = round(new_salary, 2)
                players_updated += 1
                
                # Logger les changements significatifs (>10%)
                change_pct = abs((new_salary - old_salary) / old_salary) * 100
                if change_pct > 10:
                    direction = "📈" if new_salary > old_salary else "📉"
                    logger.info(
                        f"{direction} {player.full_name}: "
                        f"${old_salary/1_000_000:.1f}M → ${new_salary/1_000_000:.1f}M "
                        f"({change_pct:+.1f}%) - Avg: {avg_score:.1f}"
                    )
                
                # Commit toutes les 100 joueurs
                if players_updated % 100 == 0:
                    db.commit()
                    logger.info(f"💾 {players_updated} joueurs mis à jour...")
                
            except Exception as e:
                logger.error(f"   ❌ Erreur pour {player.full_name} : {e}")
                continue
        
        # Commit final
        db.commit()
        
        # Statistiques finales
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"✅ MISE À JOUR TERMINÉE")
        logger.info(f"   Salaires mis à jour : {players_updated}")
        logger.info(f"   Joueurs ignorés (< 5 matchs) : {players_skipped}")
        logger.info(f"   Total traité : {players_updated + players_skipped}/{len(players)}")
        
        # Top 5 des salaires les plus élevés
        top_salaries = db.query(Player).filter(
            Player.is_active == True
        ).order_by(Player.fantasy_cost.desc()).limit(5).all()
        
        logger.info("")
        logger.info("💎 TOP 5 DES SALAIRES :")
        for i, p in enumerate(top_salaries, 1):
            logger.info(f"   {i}. {p.full_name} ({p.position}) : ${p.fantasy_cost/1_000_000:.1f}M")
        
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la mise à jour des salaires : {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    # Pour tester la tâche manuellement
    logging.basicConfig(level=logging.INFO)
    update_all_player_salaries()

"""
Tâche : Traitement des demandes de transfert (Waiver Wire)
Exécution : Tous les lundis à 13h00

Traite toutes les demandes de transfert en attente pour les ligues privées
Attribution selon l'ordre de priorité (waiver priority)
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.core.database import SessionLocal
from app.models.league import League, LeagueType
from app.models.fantasy_team import FantasyTeam
from app.models.fantasy_team_player import FantasyTeamPlayer
from app.models.transfer import Transfer, TransferStatus, TransferType
from app.models.player import Player

logger = logging.getLogger(__name__)


def process_waiver_claims():
    """
    Traite les demandes de waiver pour les ligues privées
    
    Processus (pour chaque ligue privée) :
    1. Récupère toutes les demandes PENDING triées par waiver_priority
    2. Pour chaque demande :
       - Vérifie que le joueur est toujours disponible
       - Vérifie le salary cap
       - Si OK : exécute le transfert (drop + add)
       - Si KO : refuse la demande
    3. Met à jour la waiver_priority (dernier servi passe en dernier)
    
    Note : Dans les ligues privées, chaque joueur ne peut appartenir
           qu'à une seule équipe (joueurs uniques)
    """
    logger.info("=" * 80)
    logger.info("🔄 TRAITEMENT DES WAIVERS - DÉBUT")
    logger.info("=" * 80)
    
    db: Session = SessionLocal()
    total_claims_processed = 0
    total_claims_granted = 0
    total_claims_denied = 0
    
    try:
        # Récupérer toutes les ligues privées actives
        private_leagues = db.query(League).filter(
            and_(
                League.type == LeagueType.PRIVATE,
                League.is_active == True
            )
        ).all()
        
        logger.info(f"🏆 {len(private_leagues)} ligues privées à traiter")
        
        for league in private_leagues:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"🏆 Ligue : {league.name}")
            logger.info(f"{'=' * 60}")
            
            # Récupérer toutes les demandes en attente
            pending_transfers = db.query(Transfer).filter(
                and_(
                    Transfer.team_id.in_(
                        db.query(FantasyTeam.id).filter(FantasyTeam.league_id == league.id)
                    ),
                    Transfer.status == TransferStatus.PENDING
                )
            ).order_by(
                # Trier par waiver_priority de l'équipe (jointure nécessaire)
                db.query(FantasyTeam.waiver_priority).filter(
                    FantasyTeam.id == Transfer.team_id
                ).correlate(Transfer).as_scalar()
            ).all()
            
            if not pending_transfers:
                logger.info("   ℹ️  Aucune demande en attente")
                continue
            
            logger.info(f"   📋 {len(pending_transfers)} demande(s) en attente")
            
            # Traiter chaque demande dans l'ordre de priorité
            for transfer in pending_transfers:
                total_claims_processed += 1
                
                team = transfer.team
                player_in = db.query(Player).filter(Player.id == transfer.player_in_id).first()
                player_out = db.query(Player).filter(Player.id == transfer.player_out_id).first() if transfer.player_out_id else None
                
                logger.info(f"\n   👤 {team.name} (Priorité #{team.waiver_priority})")
                logger.info(f"      ➡️  Recrute : {player_in.full_name}")
                if player_out:
                    logger.info(f"      ⬅️  Libère : {player_out.full_name}")
                
                # 1. Vérifier que le joueur IN est disponible (pas déjà pris)
                existing_roster = db.query(FantasyTeamPlayer).filter(
                    and_(
                        FantasyTeamPlayer.player_id == player_in.id,
                        FantasyTeamPlayer.team_id.in_(
                            db.query(FantasyTeam.id).filter(FantasyTeam.league_id == league.id)
                        )
                    )
                ).first()
                
                if existing_roster:
                    # Joueur déjà pris par une autre équipe
                    transfer.status = TransferStatus.REJECTED
                    transfer.processed_at = datetime.now()
                    logger.warning(f"      ❌ REFUSÉ : {player_in.full_name} déjà pris")
                    total_claims_denied += 1
                    continue
                
                # 2. Calculer le nouveau salary cap
                current_cap = team.salary_cap_used or 0
                new_cap = current_cap + player_in.fantasy_cost
                if player_out:
                    new_cap -= player_out.fantasy_cost
                
                if new_cap > 60_000_000:
                    # Dépassement du salary cap
                    transfer.status = TransferStatus.REJECTED
                    transfer.processed_at = datetime.now()
                    logger.warning(
                        f"      ❌ REFUSÉ : Salary cap dépassé "
                        f"(${new_cap/1_000_000:.1f}M > $60M)"
                    )
                    total_claims_denied += 1
                    continue
                
                # 3. Exécuter le transfert
                try:
                    # Libérer le joueur OUT
                    if player_out:
                        roster_out = db.query(FantasyTeamPlayer).filter(
                            and_(
                                FantasyTeamPlayer.team_id == team.id,
                                FantasyTeamPlayer.player_id == player_out.id
                            )
                        ).first()
                        if roster_out:
                            db.delete(roster_out)
                    
                    # Ajouter le joueur IN
                    roster_in = FantasyTeamPlayer(
                        team_id=team.id,
                        player_id=player_in.id,
                        position=player_in.position,
                        added_at=datetime.now()
                    )
                    db.add(roster_in)
                    
                    # Mettre à jour le salary cap
                    team.salary_cap_used = new_cap
                    
                    # Marquer le transfert comme complété
                    transfer.status = TransferStatus.COMPLETED
                    transfer.processed_at = datetime.now()
                    
                    # Mettre l'équipe en fin de priorité (pénalité)
                    max_priority = db.query(func.max(FantasyTeam.waiver_priority)).filter(
                        FantasyTeam.league_id == league.id
                    ).scalar() or 0
                    team.waiver_priority = max_priority + 1
                    
                    logger.info(
                        f"      ✅ ACCORDÉ : ${new_cap/1_000_000:.1f}M utilisés "
                        f"(nouvelle priorité #{team.waiver_priority})"
                    )
                    total_claims_granted += 1
                    
                except Exception as e:
                    logger.error(f"      ❌ Erreur lors de l'exécution : {e}")
                    db.rollback()
                    transfer.status = TransferStatus.REJECTED
                    transfer.processed_at = datetime.now()
                    total_claims_denied += 1
            
            # Commit après chaque ligue
            db.commit()
        
        # Statistiques finales
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"✅ TRAITEMENT TERMINÉ")
        logger.info(f"   Demandes traitées : {total_claims_processed}")
        logger.info(f"   Accordées : {total_claims_granted}")
        logger.info(f"   Refusées : {total_claims_denied}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du traitement des waivers : {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    # Pour tester la tâche manuellement
    logging.basicConfig(level=logging.INFO)
    process_waiver_claims()

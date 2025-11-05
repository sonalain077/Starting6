"""
Tâche : Détection des Trades NBA
Exécution : Tous les jours à 06h00

Détecte les changements d'équipe des joueurs NBA en utilisant
nba_api pour obtenir les dernières infos d'équipe

Crée un historique des transferts dans la table PlayerTeamHistory
"""
import logging
import time
from datetime import datetime
from sqlalchemy.orm import Session
from nba_api.stats.endpoints import commonplayerinfo

from app.core.database import SessionLocal
from app.models.player import Player

logger = logging.getLogger(__name__)

def detect_nba_trades():
    """
    Détecte les trades/transferts NBA via nba_api
    
    Pour chaque joueur de notre BDD :
    1. Récupère son équipe actuelle via commonplayerinfo
    2. Compare avec l'équipe en base de données
    3. Si changement → met à jour et log le trade
    
    Note : L'historique complet sera géré par PlayerTeamHistory
          (table à créer plus tard)
    
    ⚠️ Rate limiting : 0.6s entre chaque requête (max ~100 joueurs/minute)
    """
    logger.info("=" * 80)
    logger.info("🔍 DÉTECTION DES TRADES NBA - DÉBUT")
    logger.info("=" * 80)
    
    db: Session = SessionLocal()
    trades_detected = 0
    players_checked = 0
    
    try:
        # Récupérer tous les joueurs actifs de notre BDD
        logger.info("📡 Récupération des joueurs en base...")
        
        active_players = db.query(Player).filter(
            Player.is_active == True
        ).all()
        
        logger.info(f"✅ {len(active_players)} joueurs actifs à vérifier")
        logger.info("⚠️  Vérification limitée aux 50 premiers joueurs (rate limiting)")
        
        # Limiter à 50 joueurs pour éviter les rate limits (600s = 10min max)
        # En production, on ferait ça par batch sur plusieurs heures
        check_limit = min(50, len(active_players))
        
        logger.info("🔎 Analyse des changements d'équipe...")
        today = datetime.now().date()
        
        for player in active_players[:check_limit]:
            try:
                # Rate limiting : 0.6s entre chaque requête
                time.sleep(0.6)
                
                # Récupérer les infos du joueur depuis nba_api
                player_info = commonplayerinfo.CommonPlayerInfo(player_id=player.external_api_id)
                info_df = player_info.get_data_frames()[0]
                
                if info_df.empty:
                    continue
                
                # Extraire l'équipe actuelle
                new_team = info_df['TEAM_ABBREVIATION'].values[0]
                old_team = player.team
                
                players_checked += 1
                
                if new_team != old_team and old_team != "UNK":
                    logger.info("")
                    logger.info(f"🔄 TRADE DÉTECTÉ !")
                    logger.info(f"   Joueur : {player.first_name} {player.last_name}")
                    logger.info(f"   {old_team} → {new_team}")
                    logger.info(f"   Date : {today}")
                    
                    # Mettre à jour l'équipe du joueur
                    player.team = new_team
                    player.team_abbreviation = new_team
                    
                    # TODO: Créer une entrée dans PlayerTeamHistory
                    # (à implémenter plus tard avec la table d'historique)
                    
                    trades_detected += 1
                
                # Log progression tous les 10 joueurs
                if players_checked % 10 == 0:
                    logger.info(f"   Progression : {players_checked}/{check_limit} joueurs vérifiés...")
                
            except Exception as e:
                logger.warning(f"   ⚠️  Erreur pour {player.full_name} : {e}")
                continue
        
        # Sauvegarder tous les changements
        db.commit()
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"✅ DÉTECTION TERMINÉE")
        logger.info(f"   Joueurs vérifiés : {players_checked}/{len(active_players)}")
        logger.info(f"   Trades détectés : {trades_detected}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la détection des trades : {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # Pour tester la tâche manuellement
    logging.basicConfig(level=logging.INFO)
    detect_nba_trades()

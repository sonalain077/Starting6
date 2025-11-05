"""
Tâche : Synchronisation complète des joueurs NBA
Exécution : Tous les jours à 07h00

Synchronise la liste complète des joueurs NBA depuis nba_api
Ajoute les nouveaux joueurs et met à jour les joueurs existants
"""
import logging
from sqlalchemy.orm import Session
from nba_api.stats.static import players as nba_players
from nba_api.stats.endpoints import commonplayerinfo

from app.core.database import SessionLocal
from app.models.player import Player

logger = logging.getLogger(__name__)

# Mapping pour les positions (balldontlie retourne pas toujours les bonnes positions)
POSITION_MAP = {
    "G": "SG",
    "F": "SF",
    "C": "C",
    "G-F": "SG",
    "F-C": "PF",
    "F-G": "SF",
}

def sync_nba_players():
    """
    Synchronise tous les joueurs NBA depuis nba_api
    
    Pour chaque joueur de l'API :
    1. Vérifie s'il existe déjà (par external_api_id)
    2. Si nouveau → insert
    3. Si existant → update (nom, équipe, position)
    4. Active/désactive selon le statut API
    
    Note: nba_api.stats.static.players retourne la liste complète sans API call
    """
    logger.info("=" * 80)
    logger.info("🔄 SYNCHRONISATION DES JOUEURS NBA - DÉBUT")
    logger.info("=" * 80)
    
    db: Session = SessionLocal()
    new_players = 0
    updated_players = 0
    
    try:
        # Récupérer tous les joueurs actifs depuis nba_api (local, pas de requête HTTP)
        logger.info("📡 Récupération depuis nba_api.stats.static...")
        
        all_api_players = nba_players.get_active_players()
        
        logger.info(f"✅ {len(all_api_players)} joueurs actifs récupérés")
        
        # Synchroniser chaque joueur
        logger.info("💾 Synchronisation en base de données...")
        
        for api_player in all_api_players:
            # nba_api retourne: {'id': 203507, 'full_name': 'Giannis Antetokounmpo', 'is_active': True}
            player_id = api_player["id"]
            full_name = api_player["full_name"]
            
            # Séparer prénom/nom (approximation)
            name_parts = full_name.split()
            first_name = name_parts[0] if len(name_parts) > 0 else "Unknown"
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else "Unknown"
            
            # Position par défaut (nba_api.static ne fournit pas la position)
            # On mettra SG par défaut, sera corrigé par update_salaries ou manuellement
            mapped_position = "SG"
            
            # Vérifier si le joueur existe déjà
            player = db.query(Player).filter(
                Player.external_api_id == player_id
            ).first()
            
            if player:
                # Mettre à jour le joueur existant (nom uniquement, pas l'équipe ici)
                player.first_name = first_name
                player.last_name = last_name
                player.full_name = full_name
                player.is_active = api_player.get("is_active", True)
                updated_players += 1
                
                if updated_players % 100 == 0:
                    logger.info(f"   {updated_players} joueurs mis à jour...")
            else:
                # Créer un nouveau joueur
                new_player = Player(
                    external_api_id=player_id,
                    first_name=first_name,
                    last_name=last_name,
                    full_name=full_name,
                    team="UNK",  # Sera mis à jour par detect_trades
                    team_abbreviation="UNK",
                    position=mapped_position,
                    fantasy_cost=5_000_000.0,  # Salaire par défaut de 5M$
                    is_active=api_player.get("is_active", True)
                )
                db.add(new_player)
                new_players += 1
                
                if new_players % 50 == 0:
                    logger.info(f"   {new_players} nouveaux joueurs ajoutés...")
        
        # Sauvegarder tous les changements
        db.commit()
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"✅ SYNCHRONISATION TERMINÉE")
        logger.info(f"   Nouveaux joueurs : {new_players}")
        logger.info(f"   Joueurs mis à jour : {updated_players}")
        logger.info(f"   Total : {len(all_api_players)} joueurs")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la synchronisation : {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # Pour tester la tâche manuellement
    logging.basicConfig(level=logging.INFO)
    sync_nba_players()

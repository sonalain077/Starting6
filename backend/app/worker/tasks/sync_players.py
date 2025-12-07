"""
Tâche : Synchronisation complète des joueurs NBA
Exécution : Tous les jours à 07h00

Synchronise la liste complète des joueurs NBA depuis nba_api
Ajoute les nouveaux joueurs et met à jour les joueurs existants
"""
import logging
import time
from sqlalchemy.orm import Session
from nba_api.stats.static import players as nba_players
from nba_api.stats.endpoints import commonplayerinfo

from app.core.database import SessionLocal
from app.models.player import Player

logger = logging.getLogger(__name__)

# Mapping pour les positions NBA vers nos positions standardisées
POSITION_MAP = {
    # Positions simples
    "Guard": "SG",
    "Forward": "SF",
    "Center": "C",
    "Forward-Guard": "SF",
    "Guard-Forward": "SG",
    "Forward-Center": "PF",
    "Center-Forward": "C",
    
    # Positions détaillées
    "Point Guard": "PG",
    "Shooting Guard": "SG",
    "Small Forward": "SF",
    "Power Forward": "PF",
    
    # Abréviations
    "PG": "PG",
    "SG": "SG",
    "SF": "SF",
    "PF": "PF",
    "C": "C",
    "G": "SG",
    "F": "SF",
    "G-F": "SG",
    "F-G": "SF",
    "F-C": "PF",
    "C-F": "C",
}

# Distribution cible pour assurer une couverture de tous les postes
# Si l'API ne retourne pas de position, on assigne de manière équilibrée
FALLBACK_POSITIONS = ["PG", "SG", "SF", "PF", "C"]

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
            
            # Tenter de récupérer l'équipe et la position via commonplayerinfo
            mapped_position = None
            team_abbrev = "FA"  # Free Agent par défaut
            
            try:
                # Respecter le rate limit de l'API NBA (0.6s entre chaque requête)
                time.sleep(0.6)
                info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
                info_df = info.get_data_frames()[0]
                
                if not info_df.empty:
                    # L'API NBA retourne POSITION dans la première DataFrame
                    raw_position = str(info_df['POSITION'].values[0]) if 'POSITION' in info_df else None
                    raw_team = str(info_df['TEAM_ABBREVIATION'].values[0]) if 'TEAM_ABBREVIATION' in info_df else None

                    # Mapper la position vers nos valeurs standardisées
                    if raw_position and raw_position != 'nan' and raw_position != 'None':
                        mapped_position = POSITION_MAP.get(raw_position, None)
                        if not mapped_position:
                            # Si pas de mapping exact, essayer de deviner
                            if 'Guard' in raw_position:
                                mapped_position = "PG" if 'Point' in raw_position else "SG"
                            elif 'Forward' in raw_position:
                                mapped_position = "PF" if 'Power' in raw_position else "SF"
                            elif 'Center' in raw_position:
                                mapped_position = "C"

                    if raw_team and raw_team != 'nan' and raw_team != 'None':
                        team_abbrev = raw_team
                        
            except Exception as e:
                # En cas d'erreur d'API, continuer avec les valeurs par défaut
                logger.debug(f"Erreur API pour {full_name}: {e}")
            
            # Si toujours pas de position, assigner de manière équilibrée
            if not mapped_position:
                # Utiliser le modulo pour une distribution équilibrée
                mapped_position = FALLBACK_POSITIONS[new_players % 5]
            
            # Vérifier si le joueur existe déjà
            player = db.query(Player).filter(
                Player.external_api_id == player_id
            ).first()
            
            if player:
                # Mettre à jour le joueur existant avec toutes les infos
                player.first_name = first_name
                player.last_name = last_name
                player.full_name = full_name
                player.team = team_abbrev
                player.team_abbreviation = team_abbrev
                player.position = mapped_position
                player.is_active = api_player.get("is_active", True)
                # Ne pas modifier fantasy_cost ici (sera calculé par calculate_salaries)
                updated_players += 1
                
                if updated_players % 100 == 0:
                    logger.info(f"   {updated_players} joueurs mis à jour...")
            else:
                # Créer un nouveau joueur avec salaire initial basique
                # Le salaire réel sera calculé plus tard par calculate_salaries.py
                new_player = Player(
                    external_api_id=player_id,
                    first_name=first_name,
                    last_name=last_name,
                    full_name=full_name,
                    team=team_abbrev,
                    team_abbreviation=team_abbrev,
                    position=mapped_position,
                    fantasy_cost=5_000_000,  # Salaire de départ (sera calculé après)
                    avg_fantasy_score_last_15=0.0,
                    games_played_last_20=0,
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

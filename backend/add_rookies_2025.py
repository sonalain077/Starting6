"""
Script pour ajouter manuellement les rookies de la draft 2024 (saison 2024-2025)
Ces joueurs ne sont pas toujours disponibles dans nba_api.stats.static.players
"""
import logging
import time
from sqlalchemy.orm import Session
from nba_api.stats.endpoints import commonplayerinfo

from app.core.database import SessionLocal
from app.models.player import Player

logger = logging.getLogger(__name__)

# Mapping positions
POSITION_MAP = {
    "Guard": "SG",
    "Forward": "SF",
    "Center": "C",
    "Guard-Forward": "SG",
    "Forward-Guard": "SG",
    "Forward-Center": "PF",
    "Center-Forward": "C",
    "Point Guard": "PG",
    "Shooting Guard": "SG",
    "Small Forward": "SF",
    "Power Forward": "PF",
}

# Liste des rookies 2024 (Draft June 26-27, 2024) avec leurs IDs NBA réels
ROOKIES_2024 = [
    # Top 10
    {"id": 1641705, "first_name": "Zaccharie", "last_name": "Risacher"},  # #1 ATL
    {"id": 1641713, "first_name": "Alexandre", "last_name": "Sarr"},      # #2 WAS
    {"id": 1641720, "first_name": "Reed", "last_name": "Sheppard"},       # #3 HOU
    {"id": 1641742, "first_name": "Stephon", "last_name": "Castle"},      # #4 SAS
    {"id": 1641711, "first_name": "Ron", "last_name": "Holland"},         # #5 DET
    {"id": 1641698, "first_name": "Matas", "last_name": "Buzelis"},       # #6 CHI
    {"id": 1641716, "first_name": "Donovan", "last_name": "Clingan"},     # #7 POR
    {"id": 1641717, "first_name": "Rob", "last_name": "Dillingham"},      # #8 MIN
    {"id": 1641707, "first_name": "Zach", "last_name": "Edey"},           # #9 MEM
    {"id": 1641709, "first_name": "Cody", "last_name": "Williams"},       # #10 UTA
    # Top 11-20
    {"id": 1641723, "first_name": "Matas", "last_name": "Buzelis"},       # #11
    {"id": 1641731, "first_name": "Nikola", "last_name": "Topic"},        # #12
    {"id": 1641712, "first_name": "Devin", "last_name": "Carter"},        # #13
    {"id": 1641728, "first_name": "Carlton", "last_name": "Carrington"},  # #14
    {"id": 1641714, "first_name": "Kel'el", "last_name": "Ware"},         # #15
    {"id": 1641708, "first_name": "Jared", "last_name": "McCain"},        # #16
    {"id": 1641732, "first_name": "Dalton", "last_name": "Knecht"},       # #17
    {"id": 1641729, "first_name": "Tristan", "last_name": "da Silva"},    # #18
    {"id": 1641704, "first_name": "Ja'Kobe", "last_name": "Walter"},      # #19
    {"id": 1641725, "first_name": "Kyshawn", "last_name": "George"},      # #20
]


def add_rookies_2025():
    """Ajoute les rookies 2024 dans la base"""
    db: Session = SessionLocal()
    logger.info("=" * 80)
    logger.info("🏀 AJOUT DES ROOKIES 2024 (SAISON 2024-2025)")
    logger.info("=" * 80)
    
    added = 0
    updated = 0
    errors = 0
    
    try:
        for rookie_info in ROOKIES_2024:
            try:
                player_id = rookie_info["id"]
                first_name = rookie_info["first_name"]
                last_name = rookie_info["last_name"]
                full_name = f"{first_name} {last_name}"
                
                # Vérifier si existe déjà
                existing = db.query(Player).filter(
                    Player.external_api_id == player_id
                ).first()
                
                if existing:
                    logger.info(f"⏭️  {full_name} existe déjà (ID: {player_id})")
                    continue
                
                # Récupérer position et équipe via commonplayerinfo
                time.sleep(0.6)  # Rate limiting
                logger.info(f"📡 Récupération des infos pour {full_name}...")
                
                info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
                info_df = info.get_data_frames()[0]
                
                if info_df.empty:
                    logger.warning(f"⚠️  Pas de données pour {full_name}")
                    errors += 1
                    continue
                
                raw_position = info_df.get('POSITION').values[0]
                raw_team = info_df.get('TEAM_ABBREVIATION').values[0]
                
                mapped_position = POSITION_MAP.get(raw_position, raw_position) if raw_position else "SG"
                team_abbrev = raw_team if raw_team else "UNK"
                
                # Créer le joueur
                new_player = Player(
                    external_api_id=player_id,
                    first_name=first_name,
                    last_name=last_name,
                    full_name=full_name,
                    team=team_abbrev,
                    team_abbreviation=team_abbrev,
                    position=mapped_position,
                    fantasy_cost=5_000_000.0,  # Salaire de base pour rookies
                    is_active=True
                )
                
                db.add(new_player)
                added += 1
                
                logger.info(f"✅ {full_name} ajouté ({mapped_position}, {team_abbrev})")
                
            except Exception as e:
                logger.error(f"❌ Erreur pour {rookie_info.get('first_name')} {rookie_info.get('last_name')}: {e}")
                errors += 1
                continue
        
        # Commit final
        db.commit()
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"✅ AJOUT TERMINÉ")
        logger.info(f"   Nouveaux rookies : {added}")
        logger.info(f"   Déjà existants : {len(ROOKIES_2024) - added - errors}")
        logger.info(f"   Erreurs : {errors}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Erreur globale : {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    add_rookies_2025()

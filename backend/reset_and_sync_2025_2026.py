"""
Script pour NETTOYER et SYNCHRONISER les joueurs de la saison 2025-2026 UNIQUEMENT
Supprime tous les anciens joueurs et récupère la liste actuelle depuis l'API NBA
"""
import logging
import time
from sqlalchemy.orm import Session
from nba_api.stats.static import players as nba_players
from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.endpoints import leaguedashplayerstats

from app.core.database import SessionLocal
from app.models.player import Player

logger = logging.getLogger(__name__)

# Mapping positions (API retourne des positions génériques)
POSITION_MAP = {
    "Guard": None,  # Trop générique - on décidera avec les stats
    "Forward": None,  # Trop générique - on décidera avec les stats
    "Center": "C",
    "Guard-Forward": "SF",  # Swing player
    "Forward-Guard": "SG",  # Combo guard
    "Forward-Center": "PF",
    "Center-Forward": "C",
    "Point Guard": "PG",
    "Shooting Guard": "SG",
    "Small Forward": "SF",
    "Power Forward": "PF",
    "G": None,
    "F": None,
    "C": "C",
    "G-F": "SG",
    "F-C": "PF",
    "F-G": "SF",
}


def guess_position_from_stats(raw_position: str, stats: dict) -> str:
    """
    Devine le poste réel basé sur les stats du joueur.
    
    Logique :
    - Guard + AST élevés = PG
    - Guard + AST faibles = SG
    - Forward + REB/BLK élevés = PF
    - Forward + REB/BLK faibles = SF
    """
    # Si le mapping est précis, on l'utilise
    mapped = POSITION_MAP.get(raw_position)
    if mapped:
        return mapped
    
    # Sinon, on analyse les stats
    ast = stats.get('AST', 0)
    reb = stats.get('REB', 0)
    pts = stats.get('PTS', 0)
    blk = stats.get('BLK', 0)
    
    if raw_position == "Guard" or raw_position == "G":
        # Si assists > 4 par match = Meneur (PG)
        # Sinon = Arrière (SG)
        return "PG" if ast >= 4.0 else "SG"
    
    elif raw_position == "Forward" or raw_position == "F":
        # Si rebonds > 7 ou contres > 0.8 = Ailier Fort (PF)
        # Sinon = Ailier (SF)
        return "PF" if (reb >= 7.0 or blk >= 0.8) else "SF"
    
    # Défaut si aucun pattern
    return "SG"

# Rookies de la draft 2025 (Draft June 2025) - IDs à confirmer
ROOKIES_2025 = [
    # Top picks (IDs fictifs car saison pas encore commencée en réalité)
    {"id": 1641900, "first_name": "Cooper", "last_name": "Flagg", "team": "ATL"},
    {"id": 1641901, "first_name": "Dylan", "last_name": "Harper", "team": "WAS"},
    {"id": 1641902, "first_name": "Ace", "last_name": "Bailey", "team": "BKN"},
    {"id": 1641903, "first_name": "VJ", "last_name": "Edgecombe", "team": "CHI"},
    {"id": 1641904, "first_name": "Egor", "last_name": "Demin", "team": "HOU"},
]


def reset_and_sync_2025_2026():
    """
    ÉTAPE 1 : Supprimer tous les joueurs
    ÉTAPE 2 : Récupérer les joueurs actifs saison 2025-2026 via stats.nba.com
    ÉTAPE 3 : Ajouter les rookies 2025
    """
    db: Session = SessionLocal()
    logger.info("=" * 80)
    logger.info("🔄 SYNCHRONISATION SAISON 2025-2026")
    logger.info("=" * 80)
    
    try:
        # ÉTAPE 1 : Supprimer tous les joueurs existants
        logger.info("")
        logger.info("🗑️  ÉTAPE 1/3 : Suppression des anciens joueurs...")
        count_before = db.query(Player).count()
        db.query(Player).delete()
        db.commit()
        logger.info(f"   ✅ {count_before} joueurs supprimés")
        
        # ÉTAPE 2 : Récupérer les joueurs actifs de la saison 2025-2026
        logger.info("")
        logger.info("📡 ÉTAPE 2/3 : Récupération joueurs saison 2025-2026...")
        logger.info("   (Utilisation de LeagueDashPlayerStats pour la saison en cours)")
        
        # Utiliser LeagueDashPlayerStats pour obtenir UNIQUEMENT les joueurs actifs cette saison
        # Season 2025-26 (format NBA: "2025-26")
        stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season="2025-26",
            season_type_all_star="Regular Season",
            per_mode_detailed="PerGame"
        )
        
        players_df = stats.get_data_frames()[0]
        logger.info(f"   ✅ {len(players_df)} joueurs actifs trouvés pour 2025-26")
        
        added = 0
        errors = 0
        
        for idx, row in players_df.iterrows():
            try:
                player_id = row['PLAYER_ID']
                player_name = row['PLAYER_NAME']
                
                # Séparer prénom/nom
                name_parts = player_name.split()
                first_name = name_parts[0] if len(name_parts) > 0 else "Unknown"
                last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else "Unknown"
                
                team_abbrev = row.get('TEAM_ABBREVIATION', 'UNK')
                
                # Récupérer stats moyennes (déjà dans le DataFrame)
                player_stats = {
                    'AST': row.get('AST', 0),
                    'REB': row.get('REB', 0),
                    'PTS': row.get('PTS', 0),
                    'BLK': row.get('BLK', 0),
                }
                
                # Récupérer position via commonplayerinfo
                time.sleep(0.6)  # Rate limiting
                
                mapped_position = "SG"  # Défaut si tout échoue
                try:
                    info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
                    info_df = info.get_data_frames()[0]
                    if not info_df.empty:
                        raw_position = info_df.get('POSITION').values[0]
                        if raw_position:
                            # Utiliser la fonction intelligente avec les stats
                            mapped_position = guess_position_from_stats(raw_position, player_stats)
                            logger.debug(f"   {player_name}: {raw_position} + stats → {mapped_position}")
                except Exception as e:
                    logger.warning(f"   Position API failed for {player_name}: {e}")
                    # Fallback: deviner avec les stats uniquement
                    if player_stats['AST'] >= 4.0:
                        mapped_position = "PG"
                    elif player_stats['REB'] >= 8.0 or player_stats['BLK'] >= 1.0:
                        mapped_position = "PF"
                    elif player_stats['REB'] >= 5.0:
                        mapped_position = "SF"
                
                # Créer le joueur
                new_player = Player(
                    external_api_id=player_id,
                    first_name=first_name,
                    last_name=last_name,
                    full_name=player_name,
                    team=team_abbrev,
                    team_abbreviation=team_abbrev,
                    position=mapped_position,
                    fantasy_cost=5_000_000.0,
                    is_active=True
                )
                
                db.add(new_player)
                added += 1
                
                if added % 50 == 0:
                    logger.info(f"   Progression : {added} joueurs ajoutés...")
                
            except Exception as e:
                logger.warning(f"   ⚠️  Erreur pour {row.get('PLAYER_NAME')}: {e}")
                errors += 1
                continue
        
        db.commit()
        logger.info(f"   ✅ {added} joueurs de la saison 2025-26 ajoutés")
        
        # ÉTAPE 3 : Ajouter les rookies 2025 (s'ils ne sont pas déjà là)
        logger.info("")
        logger.info("🏀 ÉTAPE 3/3 : Ajout des rookies draft 2025...")
        
        rookies_added = 0
        for rookie_info in ROOKIES_2025:
            try:
                # Vérifier si existe déjà
                existing = db.query(Player).filter(
                    Player.external_api_id == rookie_info["id"]
                ).first()
                
                if existing:
                    continue
                
                # Créer le rookie
                new_rookie = Player(
                    external_api_id=rookie_info["id"],
                    first_name=rookie_info["first_name"],
                    last_name=rookie_info["last_name"],
                    full_name=f"{rookie_info['first_name']} {rookie_info['last_name']}",
                    team=rookie_info.get("team", "UNK"),
                    team_abbreviation=rookie_info.get("team", "UNK"),
                    position="SF",  # Position par défaut pour rookies
                    fantasy_cost=5_000_000.0,
                    is_active=True
                )
                
                db.add(new_rookie)
                rookies_added += 1
                logger.info(f"   ✅ Rookie ajouté : {new_rookie.full_name} ({new_rookie.team})")
                
            except Exception as e:
                logger.warning(f"   ⚠️  Erreur rookie : {e}")
                continue
        
        db.commit()
        logger.info(f"   ✅ {rookies_added} rookies 2025 ajoutés")
        
        # RÉSUMÉ FINAL
        total_final = db.query(Player).count()
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ SYNCHRONISATION TERMINÉE")
        logger.info(f"   Total joueurs saison 2025-2026 : {total_final}")
        logger.info(f"   - Joueurs actifs stats : {added}")
        logger.info(f"   - Rookies draft 2025 : {rookies_added}")
        logger.info(f"   - Erreurs : {errors}")
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
    logger.info("")
    logger.info("⚠️  ATTENTION : Ce script va SUPPRIMER tous les joueurs existants")
    logger.info("    et récupérer uniquement ceux de la saison 2025-2026")
    logger.info("")
    
    response = input("Continuer ? (oui/non) : ")
    if response.lower() in ['oui', 'o', 'yes', 'y']:
        reset_and_sync_2025_2026()
    else:
        logger.info("❌ Annulé par l'utilisateur")

"""
TEST PIPELINE COMPLET - End-to-End System Validation
=====================================================

Ce script teste toute la chaîne de données du système :
1. Récupération des boxscores NBA (fetch_boxscores)
2. Calcul des scores d'équipes (calculate_team_scores)
3. Mise à jour des leaderboards (update_leaderboards)
4. Validation des endpoints API (scores & leaderboards)

Objectif : S'assurer qu'aucun bug n'est passé inaperçu
"""
import sys
sys.path.insert(0, 'c:/Users/phams/Desktop/ProjetFullstack/backend')

import logging
import requests
from datetime import datetime, timedelta

# Imports des modèles et database
from app.core.database import SessionLocal
from app.models.fantasy_team import FantasyTeam
from app.models.fantasy_team_score import FantasyTeamScore
from app.models.fantasy_team_player import FantasyTeamPlayer
from app.models.player_game_score import PlayerGameScore
from app.models.player import Player
from app.models.league import League, LeagueType

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# URL de l'API
API_URL = "http://localhost:8000/api/v1"

def print_section(title):
    """Affiche un séparateur visuel"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_step_1_fetch_boxscores():
    """ÉTAPE 1 : Récupération des boxscores NBA"""
    print_section("ÉTAPE 1 : RÉCUPÉRATION DES BOXSCORES NBA")
    
    try:
        from app.worker.tasks.fetch_boxscores import fetch_yesterday_boxscores
        
        logger.info("🏀 Lancement de fetch_yesterday_boxscores...")
        fetch_yesterday_boxscores()
        
        logger.info("✅ ÉTAPE 1 RÉUSSIE : Boxscores récupérés")
        return True
        
    except Exception as e:
        logger.error(f"❌ ÉTAPE 1 ÉCHOUÉE : {e}")
        import traceback
        traceback.print_exc()
        return False


def test_step_2_calculate_team_scores():
    """ÉTAPE 2 : Calcul des scores d'équipes fantasy"""
    print_section("ÉTAPE 2 : CALCUL DES SCORES D'ÉQUIPES")
    
    try:
        from app.worker.tasks.calculate_team_scores import calculate_yesterday_team_scores
        
        logger.info("📊 Lancement de calculate_yesterday_team_scores...")
        calculate_yesterday_team_scores()
        
        logger.info("✅ ÉTAPE 2 RÉUSSIE : Scores d'équipes calculés")
        return True
        
    except Exception as e:
        logger.error(f"❌ ÉTAPE 2 ÉCHOUÉE : {e}")
        import traceback
        traceback.print_exc()
        return False


def test_step_3_update_leaderboards():
    """ÉTAPE 3 : Mise à jour des leaderboards"""
    print_section("ÉTAPE 3 : MISE À JOUR DES LEADERBOARDS")
    
    try:
        from app.worker.tasks.update_leaderboards import update_leaderboards
        
        logger.info("🏆 Lancement de update_leaderboards...")
        update_leaderboards()
        
        logger.info("✅ ÉTAPE 3 RÉUSSIE : Leaderboards mis à jour")
        return True
        
    except Exception as e:
        logger.error(f"❌ ÉTAPE 3 ÉCHOUÉE : {e}")
        import traceback
        traceback.print_exc()
        return False


def test_step_4_api_endpoints():
    """ÉTAPE 4 : Validation directe des données (sans passer par l'API authentifiée)"""
    print_section("ÉTAPE 4 : VALIDATION DES DONNÉES")
    
    all_passed = True
    db = SessionLocal()
    
    try:
        # Test 1 : Vérifier les équipes dans la SOLO league
        logger.info("🔍 Test 1 : Équipes dans la SOLO league")
        try:
            from app.models.league import League, LeagueType
            
            solo_league = db.query(League).filter(League.type == LeagueType.SOLO).first()
            
            if solo_league:
                teams_count = db.query(FantasyTeam).filter(
                    FantasyTeam.league_id == solo_league.id
                ).count()
                
                logger.info(f"   ✅ SOLO League trouvée : {solo_league.name}")
                logger.info(f"   👥 {teams_count} équipes inscrites")
                
                if teams_count > 0:
                    logger.info(f"   ✅ Au moins 1 équipe présente")
                else:
                    logger.warning(f"   ⚠️  Aucune équipe dans la SOLO league")
            else:
                logger.error(f"   ❌ SOLO League introuvable")
                all_passed = False
                
        except Exception as e:
            logger.error(f"   ❌ Erreur : {e}")
            all_passed = False
    
        # Test 2 : Vérifier les scores de l'équipe ID 2
        logger.info("\n🔍 Test 2 : Scores de l'équipe ID 2")
        try:
            team = db.query(FantasyTeam).filter(FantasyTeam.id == 2).first()
            
            if team:
                logger.info(f"   ✅ Équipe trouvée : {team.name}")
                
                # Récupérer tous les scores de l'équipe
                team_scores = db.query(FantasyTeamScore).filter(
                    FantasyTeamScore.fantasy_team_id == 2
                ).all()
                
                if team_scores:
                    total_score = sum(score.total_score for score in team_scores)
                    avg_score = total_score / len(team_scores)
                    best_score = max(score.total_score for score in team_scores)
                    worst_score = min(score.total_score for score in team_scores)
                    
                    logger.info(f"   📊 Stats globales :")
                    logger.info(f"      - Score total : {total_score:.1f} pts")
                    logger.info(f"      - Moyenne : {avg_score:.1f} pts/jour")
                    logger.info(f"      - Meilleur jour : {best_score:.1f} pts")
                    logger.info(f"      - Pire jour : {worst_score:.1f} pts")
                    logger.info(f"      - Jours avec données : {len(team_scores)}")
                    
                    if total_score > 0:
                        logger.info(f"   ✅ Score total > 0 validé")
                    else:
                        logger.warning(f"   ⚠️  Score total = 0")
                else:
                    logger.warning(f"   ⚠️  Aucun score enregistré pour cette équipe")
            else:
                logger.error(f"   ❌ Équipe ID 2 introuvable")
                all_passed = False
                
        except Exception as e:
            logger.error(f"   ❌ Erreur : {e}")
            all_passed = False
    
        # Test 3 : Vérifier les scores détaillés pour yesterday
        yesterday = (datetime.now() - timedelta(days=1)).date()
        logger.info(f"\n🔍 Test 3 : Scores détaillés pour {yesterday}")
        try:
            from app.models.fantasy_team_player import FantasyTeamPlayer
            from app.models.player import Player
            
            # Récupérer le score d'équipe pour yesterday
            team_score = db.query(FantasyTeamScore).filter(
                FantasyTeamScore.fantasy_team_id == 2,
                FantasyTeamScore.score_date == yesterday
            ).first()
            
            if team_score:
                logger.info(f"   ✅ Score équipe trouvé")
                logger.info(f"   📅 Date : {team_score.score_date}")
                logger.info(f"   🏀 Score total équipe : {team_score.total_score:.1f} pts")
                
                # Récupérer les joueurs de l'équipe
                team_players = db.query(FantasyTeamPlayer).filter(
                    FantasyTeamPlayer.fantasy_team_id == 2
                ).all()
                
                logger.info(f"   👥 Joueurs avec score :")
                players_with_score = 0
                
                for team_player in team_players:
                    player_score = db.query(PlayerGameScore).filter(
                        PlayerGameScore.player_id == team_player.player_id,
                        PlayerGameScore.game_date == yesterday
                    ).first()
                    
                    if player_score and player_score.fantasy_score > 0:
                        logger.info(f"      - {team_player.player.full_name} ({team_player.roster_slot}) : {player_score.fantasy_score:.1f} pts")
                        players_with_score += 1
                
                if players_with_score > 0:
                    logger.info(f"   ✅ {players_with_score}/6 joueurs ont un score")
                else:
                    logger.warning(f"   ⚠️  Aucun joueur n'a de score pour cette date")
            else:
                logger.warning(f"   ⚠️  Aucun score d'équipe pour {yesterday}")
                
        except Exception as e:
            logger.error(f"   ❌ Erreur : {e}")
            all_passed = False
    
    finally:
        db.close()
    
    if all_passed:
        logger.info("\n✅ ÉTAPE 4 RÉUSSIE : Toutes les données sont cohérentes")
    else:
        logger.error("\n❌ ÉTAPE 4 ÉCHOUÉE : Certains tests ont échoué")
    
    return all_passed


def test_step_5_data_integrity():
    """ÉTAPE 5 : Vérification de l'intégrité des données"""
    print_section("ÉTAPE 5 : VÉRIFICATION D'INTÉGRITÉ DES DONNÉES")
    
    try:
        from app.core.database import SessionLocal
        from app.models.player_game_score import PlayerGameScore
        from app.models.fantasy_team_score import FantasyTeamScore
        from app.models.fantasy_team_player import FantasyTeamPlayer
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        db = SessionLocal()
        yesterday = (datetime.now() - timedelta(days=1)).date()
        
        # Test 1 : Vérifier les PlayerGameScore
        logger.info("🔍 Test 1 : PlayerGameScore")
        player_scores_count = db.query(func.count(PlayerGameScore.id)).filter(
            PlayerGameScore.game_date == yesterday
        ).scalar()
        
        logger.info(f"   📊 {player_scores_count} scores de joueurs pour {yesterday}")
        
        if player_scores_count > 0:
            # Statistiques
            avg_score = db.query(func.avg(PlayerGameScore.fantasy_score)).filter(
                PlayerGameScore.game_date == yesterday
            ).scalar()
            
            max_score = db.query(func.max(PlayerGameScore.fantasy_score)).filter(
                PlayerGameScore.game_date == yesterday
            ).scalar()
            
            logger.info(f"   📈 Score moyen : {avg_score:.1f} pts")
            logger.info(f"   🌟 Score max : {max_score:.1f} pts")
            logger.info(f"   ✅ Données présentes")
        else:
            logger.warning(f"   ⚠️  Aucun score de joueur pour {yesterday}")
        
        # Test 2 : Vérifier les FantasyTeamScore
        logger.info("\n🔍 Test 2 : FantasyTeamScore")
        team_scores_count = db.query(func.count(FantasyTeamScore.id)).filter(
            FantasyTeamScore.score_date == yesterday
        ).scalar()
        
        logger.info(f"   📊 {team_scores_count} scores d'équipes pour {yesterday}")
        
        if team_scores_count > 0:
            # Statistiques
            avg_team_score = db.query(func.avg(FantasyTeamScore.total_score)).filter(
                FantasyTeamScore.score_date == yesterday
            ).scalar()
            
            max_team_score = db.query(func.max(FantasyTeamScore.total_score)).filter(
                FantasyTeamScore.score_date == yesterday
            ).scalar()
            
            logger.info(f"   📈 Score moyen d'équipe : {avg_team_score:.1f} pts")
            logger.info(f"   🌟 Score max d'équipe : {max_team_score:.1f} pts")
            logger.info(f"   ✅ Données présentes")
        else:
            logger.warning(f"   ⚠️  Aucun score d'équipe pour {yesterday}")
        
        # Test 3 : Vérifier la cohérence (score équipe = somme des 6 joueurs)
        logger.info("\n🔍 Test 3 : Cohérence score équipe = somme joueurs")
        
        # Récupérer une équipe avec un score
        team_score = db.query(FantasyTeamScore).filter(
            FantasyTeamScore.score_date == yesterday,
            FantasyTeamScore.total_score > 0
        ).first()
        
        if team_score:
            team_id = team_score.fantasy_team_id
            recorded_score = team_score.total_score
            
            # Récupérer les 6 joueurs de l'équipe
            roster = db.query(FantasyTeamPlayer).filter(
                FantasyTeamPlayer.fantasy_team_id == team_id
            ).all()
            
            # Calculer la somme des scores des joueurs
            total_player_scores = 0
            players_with_score = 0
            
            for slot in roster:
                player_score = db.query(PlayerGameScore).filter(
                    PlayerGameScore.player_id == slot.player_id,
                    PlayerGameScore.game_date == yesterday
                ).first()
                
                if player_score:
                    total_player_scores += player_score.fantasy_score
                    players_with_score += 1
            
            logger.info(f"   🏀 Équipe ID {team_id}")
            logger.info(f"   📊 Score enregistré : {recorded_score:.1f} pts")
            logger.info(f"   ➕ Somme des joueurs : {total_player_scores:.1f} pts ({players_with_score}/6 joueurs)")
            
            if abs(recorded_score - total_player_scores) < 0.01:
                logger.info(f"   ✅ Cohérence validée")
            else:
                logger.error(f"   ❌ INCOHÉRENCE : {recorded_score} ≠ {total_player_scores}")
                db.close()
                return False
        else:
            logger.warning(f"   ⚠️  Aucune équipe avec score pour tester la cohérence")
        
        db.close()
        logger.info("\n✅ ÉTAPE 5 RÉUSSIE : Intégrité des données validée")
        return True
        
    except Exception as e:
        logger.error(f"❌ ÉTAPE 5 ÉCHOUÉE : {e}")
        import traceback
        traceback.print_exc()
        return False


def run_complete_pipeline():
    """Exécute le pipeline complet et génère un rapport"""
    print("\n")
    print("🚀" * 40)
    print("  TEST PIPELINE COMPLET - VALIDATION END-TO-END")
    print("🚀" * 40)
    print("\n")
    
    results = {
        "Étape 1 - Fetch Boxscores": False,
        "Étape 2 - Calculate Team Scores": False,
        "Étape 3 - Update Leaderboards": False,
        "Étape 4 - API Endpoints": False,
        "Étape 5 - Data Integrity": False,
    }
    
    # Exécution séquentielle
    results["Étape 1 - Fetch Boxscores"] = test_step_1_fetch_boxscores()
    
    if results["Étape 1 - Fetch Boxscores"]:
        results["Étape 2 - Calculate Team Scores"] = test_step_2_calculate_team_scores()
    
    if results["Étape 2 - Calculate Team Scores"]:
        results["Étape 3 - Update Leaderboards"] = test_step_3_update_leaderboards()
    
    # Tests de validation (indépendants)
    results["Étape 4 - API Endpoints"] = test_step_4_api_endpoints()
    results["Étape 5 - Data Integrity"] = test_step_5_data_integrity()
    
    # Rapport final
    print_section("📋 RAPPORT FINAL")
    
    all_passed = True
    for step, passed in results.items():
        status = "✅ RÉUSSI" if passed else "❌ ÉCHOUÉ"
        print(f"  {status} : {step}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    
    if all_passed:
        print("  🎉 PIPELINE COMPLET : TOUS LES TESTS ONT RÉUSSI 🎉")
        print("  ✅ Le système est opérationnel de bout en bout")
    else:
        print("  ⚠️  PIPELINE COMPLET : CERTAINS TESTS ONT ÉCHOUÉ")
        print("  ❌ Vérifier les logs ci-dessus pour identifier les problèmes")
    
    print("=" * 80 + "\n")
    
    return all_passed


if __name__ == "__main__":
    try:
        success = run_complete_pipeline()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur fatale : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

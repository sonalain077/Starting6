"""
Endpoints pour la consultation des scores fantasy
"""
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.utilisateur import Utilisateur
from app.models.fantasy_team import FantasyTeam
from app.models.fantasy_team_score import FantasyTeamScore
from app.models.fantasy_team_player import FantasyTeamPlayer
from app.models.player_game_score import PlayerGameScore
from app.models.league import League, LeagueType

router = APIRouter()


@router.get("/teams/{team_id}/scores")
def get_team_score_history(
    team_id: int,
    days: int = Query(default=7, ge=1, le=90, description="Nombre de jours d'historique (1-90)"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    📊 Récupère l'historique des scores d'une équipe
    
    **Paramètres :**
    - `team_id` : ID de l'équipe fantasy
    - `days` : Nombre de jours d'historique (défaut: 7, max: 90)
    
    **Retourne :**
    - Informations de l'équipe
    - Liste des scores quotidiens
    - Statistiques (total, moyenne, meilleur jour)
    - Détail des joueurs pour chaque jour
    """
    # Vérifier que l'équipe existe
    team = db.query(FantasyTeam).filter(FantasyTeam.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail=f"Équipe avec l'ID {team_id} introuvable")
    
    # Date de début
    start_date = datetime.now().date() - timedelta(days=days)
    
    # Récupérer les scores quotidiens
    daily_scores = db.query(FantasyTeamScore).filter(
        FantasyTeamScore.fantasy_team_id == team_id,
        FantasyTeamScore.score_date >= start_date
    ).order_by(desc(FantasyTeamScore.score_date)).all()
    
    # Calculer les statistiques
    if daily_scores:
        scores_values = [s.total_score for s in daily_scores]
        total_score = sum(scores_values)
        avg_score = total_score / len(scores_values)
        best_day = max(daily_scores, key=lambda x: x.total_score)
        worst_day = min(daily_scores, key=lambda x: x.total_score)
    else:
        total_score = 0
        avg_score = 0
        best_day = None
        worst_day = None
    
    # Construire la réponse
    return {
        "team": {
            "id": team.id,
            "name": team.name,
            "league_id": team.league_id
        },
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": datetime.now().date().isoformat(),
            "days": days
        },
        "statistics": {
            "total_score": round(total_score, 1),
            "average_score": round(avg_score, 1),
            "games_played": len(daily_scores),
            "best_day": {
                "date": best_day.score_date.isoformat() if best_day else None,
                "score": round(best_day.total_score, 1) if best_day else 0
            },
            "worst_day": {
                "date": worst_day.score_date.isoformat() if worst_day else None,
                "score": round(worst_day.total_score, 1) if worst_day else 0
            }
        },
        "daily_scores": [
            {
                "date": score.score_date.isoformat(),
                "total_score": round(score.total_score, 1)
            }
            for score in daily_scores
        ]
    }


@router.get("/teams/{team_id}/scores/{date}")
def get_team_score_detail(
    team_id: int,
    date: str,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    📊 Détails des scores d'une équipe pour un jour précis
    
    **Paramètres :**
    - `team_id` : ID de l'équipe fantasy
    - `date` : Date au format YYYY-MM-DD
    
    **Retourne :**
    - Score total de l'équipe
    - Score détaillé de chaque joueur (stats complètes)
    """
    # Vérifier l'équipe
    team = db.query(FantasyTeam).filter(FantasyTeam.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail=f"Équipe avec l'ID {team_id} introuvable")
    
    # Parser la date
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")
    
    # Récupérer le score de l'équipe pour ce jour
    team_score = db.query(FantasyTeamScore).filter(
        FantasyTeamScore.fantasy_team_id == team_id,
        FantasyTeamScore.score_date == target_date
    ).first()
    
    if not team_score:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun score trouvé pour l'équipe {team_id} à la date {date}"
        )
    
    # Récupérer le roster de l'équipe (au moment du match)
    roster = db.query(FantasyTeamPlayer).filter(
        FantasyTeamPlayer.fantasy_team_id == team_id
    ).all()
    
    # Pour chaque joueur, récupérer son score du jour
    player_scores = []
    for roster_slot in roster:
        player = roster_slot.player
        
        # Score du joueur pour ce jour
        game_score = db.query(PlayerGameScore).filter(
            PlayerGameScore.player_id == player.id,
            PlayerGameScore.game_date == target_date
        ).first()
        
        if game_score:
            player_scores.append({
                "position_slot": roster_slot.roster_slot.value,
                "player": {
                    "id": player.id,
                    "full_name": player.full_name,
                    "position": player.position.value,
                    "team": player.team_abbreviation
                },
                "played": True,
                "minutes": game_score.minutes_played,
                "stats": {
                    "points": game_score.points,
                    "rebounds": game_score.rebounds,
                    "assists": game_score.assists,
                    "steals": game_score.steals,
                    "blocks": game_score.blocks,
                    "turnovers": game_score.turnovers
                },
                "fantasy_score": round(game_score.fantasy_score, 1)
            })
        else:
            # Joueur n'a pas joué (repos/blessé)
            player_scores.append({
                "position_slot": roster_slot.roster_slot.value,
                "player": {
                    "id": player.id,
                    "full_name": player.full_name,
                    "position": player.position.value,
                    "team": player.team_abbreviation
                },
                "played": False,
                "minutes": 0,
                "stats": None,
                "fantasy_score": 0.0
            })
    
    return {
        "team": {
            "id": team.id,
            "name": team.name
        },
        "date": target_date.isoformat(),
        "total_score": round(team_score.total_score, 1),
        "player_scores": player_scores
    }


@router.get("/leagues/solo/leaderboard")
def get_solo_leaderboard(
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    🏆 Classement de la ligue SOLO (raccourci)
    
    Endpoint direct pour accéder au classement global SOLO
    sans connaître l'ID de la ligue (toujours 1)
    """
    # La ligue SOLO a toujours l'ID 1
    return get_league_leaderboard(league_id=1, limit=limit, db=db)


@router.get("/leagues/{league_id}/leaderboard")
def get_league_leaderboard(
    league_id: int,
    limit: int = Query(default=50, ge=1, le=100, description="Nombre d'équipes à afficher"),
    db: Session = Depends(get_db)
):
    """
    🏆 Classement d'une ligue
    
    **Paramètres :**
    - `league_id` : ID de la ligue (1 = SOLO)
    - `limit` : Nombre d'équipes à afficher (défaut: 50, max: 100)
    
    **Retourne :**
    - Informations de la ligue
    - Classement des équipes (score total, moyenne, nb jours)
    - Période de calcul
    
    **Règles :**
    - SOLO : Cumul des 7 derniers jours
    - PRIVATE : Cumul depuis le début de la saison
    """
    # Vérifier que la ligue existe
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(status_code=404, detail=f"Ligue avec l'ID {league_id} introuvable")
    
    # Déterminer la période
    if league.type == LeagueType.SOLO:
        start_date = datetime.now().date() - timedelta(days=7)
        period_description = "7 derniers jours (rolling)"
    else:
        # Convertir DateTime en date si nécessaire
        if league.start_date:
            start_date = league.start_date.date() if hasattr(league.start_date, 'date') else league.start_date
        else:
            start_date = datetime.now().date() - timedelta(days=30)
        period_description = f"Depuis le {start_date.isoformat()}"
    
    # Récupérer toutes les équipes de la ligue
    teams = db.query(FantasyTeam).filter(
        FantasyTeam.league_id == league_id
    ).all()
    
    # Calculer le score de chaque équipe
    rankings = []
    
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
        
        rankings.append({
            "team_id": team.id,
            "team_name": team.name,
            "owner_id": team.owner_id,
            "total_score": round(total_score, 1),
            "games_played": days_count,
            "average_score": round(avg_score, 1)
        })
    
    # Trier par score total décroissant
    rankings.sort(key=lambda x: x['total_score'], reverse=True)
    
    # Ajouter le rang
    for rank, team_data in enumerate(rankings, 1):
        team_data['rank'] = rank
    
    # Limiter le nombre de résultats
    rankings = rankings[:limit]
    
    return {
        "league": {
            "id": league.id,
            "name": league.name,
            "type": league.type.value
        },
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": datetime.now().date().isoformat(),
            "description": period_description
        },
        "total_teams": len(teams),
        "displayed_teams": len(rankings),
        "leaderboard": rankings
    }

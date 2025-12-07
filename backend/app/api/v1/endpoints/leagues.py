"""
Endpoints API pour les Ligues (Leagues)

Ces endpoints permettent de :
- Créer une nouvelle ligue
- Lister toutes les ligues
- Obtenir les détails d'une ligue

URL de base : /api/v1/leagues
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.league import League, LeagueType
from app.models.utilisateur import Utilisateur
from app.schemas.league import (
    LeagueCreate,
    LeagueRead,
    LeagueUpdate,
    LeagueList
)
from app.core.auth import get_current_user

# Créer le router FastAPI
router = APIRouter()


@router.post("/", response_model=LeagueRead, status_code=status.HTTP_201_CREATED)
def create_league(
    league_data: LeagueCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Créer une nouvelle ligue
    
    **Endpoint :** POST /api/v1/leagues
    
    **Authentification requise :** Oui (JWT token)
    
    **Body (JSON) :**
    ```json
    {
        "name": "Ma Super Ligue",
        "type": "PRIVATE",
        "max_teams": 10,
        "salary_cap": 60000000
    }
    ```
    
    **Réponse (JSON) :**
    ```json
    {
        "id": 1,
        "name": "Ma Super Ligue",
        "type": "PRIVATE",
        "commissioner_id": 1,
        "max_teams": 10,
        "salary_cap": 60000000,
        "is_active": true,
        "date_creation": "2025-11-02T14:30:00Z"
    }
    ```
    
    **Règles métier :**
    - Seules les ligues PRIVATE peuvent être créées via cette API
    - La ligue SOLO est unique et globale (créée automatiquement)
    - L'utilisateur connecté devient le commissaire de la ligue PRIVATE
    - max_teams est obligatoire pour PRIVATE (8-12)
    """
    
    # Note: Le schéma LeagueCreate n'a plus de champ 'type'
    # Toutes les créations via API sont PRIVATE par défaut
    
    # Validation métier : max_teams est obligatoire (entre 8 et 12)
    if league_data.max_teams is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une ligue PRIVATE doit spécifier max_teams (entre 8 et 12)"
        )
    
    # Créer l'objet League (modèle SQLAlchemy)
    # Note: type=PRIVATE par défaut, commissioner_id = utilisateur connecté
    new_league = League(
        name=league_data.name,
        type=LeagueType.PRIVATE,  # Toujours PRIVATE
        max_teams=league_data.max_teams,
        salary_cap=league_data.salary_cap,
        commissioner_id=current_user.id,  # L'utilisateur devient commissaire
        is_active=True
    )
    
    # Sauvegarder en base de données
    db.add(new_league)
    db.commit()
    db.refresh(new_league)  # Récupère l'ID auto-généré
    
    return new_league


@router.get("/solo", response_model=LeagueRead)
def get_solo_league(db: Session = Depends(get_db)):
    """
    Obtenir LA ligue SOLO globale unique
    
    **Endpoint :** GET /api/v1/leagues/solo
    
    **Authentification requise :** Non (public)
    
    **Description :**
    Retourne la ligue SOLO globale où tous les joueurs du mode SOLO sont réunis.
    Il n'existe qu'une seule ligue SOLO avec un leaderboard mondial unique.
    
    **Réponse (JSON) :**
    ```json
    {
        "id": 1,
        "name": "NBA Fantasy League - Global",
        "type": "SOLO",
        "commissioner_id": null,
        "max_teams": null,
        "salary_cap": 60000000,
        "is_active": true,
        "date_creation": "2025-11-02T14:30:00Z"
    }
    ```
    
    **Erreur 404 si la ligue SOLO n'a pas été créée (ne devrait jamais arriver).**
    """
    
    # Chercher LA ligue SOLO unique
    solo_league = db.query(League).filter(League.type == LeagueType.SOLO).first()
    
    if not solo_league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La ligue SOLO globale n'existe pas. Contactez l'administrateur."
        )
    
    return solo_league


@router.get("/", response_model=LeagueList)
def get_leagues(
    skip: int = Query(0, ge=0, description="Nombre de ligues à sauter (pagination)"),
    limit: int = Query(10, ge=1, le=100, description="Nombre max de ligues à retourner"),
    type: str = Query(None, description="Filtrer par type (SOLO ou PRIVATE)"),
    is_active: bool = Query(None, description="Filtrer par statut actif"),
    db: Session = Depends(get_db)
):
    """
    Lister toutes les ligues avec pagination et filtres
    
    **Endpoint :** GET /api/v1/leagues
    
    **Authentification requise :** Non (public)
    
    **Query Parameters :**
    - `skip` : Nombre de résultats à sauter (défaut: 0)
    - `limit` : Nombre max de résultats (défaut: 10, max: 100)
    - `type` : Filtrer par type "SOLO" ou "PRIVATE"
    - `is_active` : Filtrer par statut actif (true/false)
    
    **Exemples d'utilisation :**
    - GET /api/v1/leagues → Toutes les ligues (10 premières)
    - GET /api/v1/leagues?skip=10&limit=20 → Ligues 11 à 30
    - GET /api/v1/leagues?type=SOLO → Seulement les ligues SOLO
    - GET /api/v1/leagues?is_active=true → Seulement les ligues actives
    
    **Réponse (JSON) :**
    ```json
    {
        "total": 25,
        "leagues": [
            {
                "id": 1,
                "name": "NBA Fantasy Global",
                "type": "SOLO",
                ...
            },
            ...
        ]
    }
    ```
    """
    
    # Construire la requête de base
    query = db.query(League)
    
    # Appliquer les filtres si fournis
    if type:
        query = query.filter(League.type == type)
    
    if is_active is not None:
        query = query.filter(League.is_active == is_active)
    
    # Compter le total (avant pagination)
    total = query.count()
    
    # Appliquer la pagination
    leagues = query.offset(skip).limit(limit).all()
    
    return LeagueList(total=total, leagues=leagues)


@router.get("/{league_id}", response_model=LeagueRead)
def get_league(
    league_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtenir les détails d'une ligue spécifique
    
    **Endpoint :** GET /api/v1/leagues/{league_id}
    
    **Authentification requise :** Non (public)
    
    **Exemple :**
    - GET /api/v1/leagues/1
    
    **Réponse (JSON) :**
    ```json
    {
        "id": 1,
        "name": "NBA Fantasy Global",
        "type": "SOLO",
        "commissioner_id": null,
        "max_teams": null,
        "salary_cap": 60000000,
        "is_active": true,
        "start_date": null,
        "end_date": null,
        "date_creation": "2025-11-02T14:30:00Z"
    }
    ```
    
    **Erreur 404 si la ligue n'existe pas.**
    """
    
    # Chercher la ligue par ID
    league = db.query(League).filter(League.id == league_id).first()
    
    # Si non trouvée, retourner erreur 404
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ligue avec ID {league_id} introuvable"
        )
    
    return league


@router.patch("/{league_id}", response_model=LeagueRead)
def update_league(
    league_id: int,
    league_update: LeagueUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Modifier une ligue existante
    
    **Endpoint :** PATCH /api/v1/leagues/{league_id}
    
    **Authentification requise :** Oui (doit être le commissaire de la ligue)
    
    **Body (JSON) - Tous les champs sont optionnels :**
    ```json
    {
        "name": "Nouveau nom",
        "is_active": false
    }
    ```
    
    **Règles métier :**
    - Seul le commissaire peut modifier une ligue PRIVATE
    - Les ligues SOLO ne peuvent pas être modifiées (pas de commissaire)
    """
    
    # Chercher la ligue
    league = db.query(League).filter(League.id == league_id).first()
    
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ligue avec ID {league_id} introuvable"
        )
    
    # Vérifier les droits : seul le commissaire peut modifier
    if league.type == LeagueType.PRIVATE and league.commissioner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le commissaire peut modifier cette ligue"
        )
    
    if league.type == LeagueType.SOLO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les ligues SOLO ne peuvent pas être modifiées"
        )
    
    # Mettre à jour les champs fournis (exclude_unset ignore les champs non fournis)
    update_data = league_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(league, field, value)
    
    db.commit()
    db.refresh(league)
    
    return league


@router.get("/solo/leaderboard")
def get_solo_leaderboard(db: Session = Depends(get_db)):
    """
    Obtenir le classement de la ligue SOLO
    
    **Endpoint :** GET /api/v1/leagues/solo/leaderboard
    
    **Authentification requise :** Non (public)
    
    **Description :**
    Retourne le classement mondial de toutes les équipes en mode SOLO,
    triées par score total décroissant.
    
    **Réponse (JSON) :**
    ```json
    [
        {
            "rank": 1,
            "team_id": 5,
            "team_name": "Lakers Dream Team",
            "owner_username": "john_doe",
            "total_score": 1250.5,
            "last_7_days_score": 320.2,
            "games_played": 15,
            "average_score": 83.4,
            "trend": "up"
        },
        ...
    ]
    ```
    """
    from app.models.fantasy_team import FantasyTeam
    from app.models.fantasy_team_score import FantasyTeamScore
    from sqlalchemy import func, desc
    from datetime import datetime, timedelta
    
    # Trouver la ligue SOLO
    solo_league = db.query(League).filter(League.type == LeagueType.SOLO).first()
    
    if not solo_league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La ligue SOLO n'existe pas"
        )
    
    # Récupérer toutes les équipes de la ligue SOLO avec leurs scores
    teams_query = db.query(
        FantasyTeam.id,
        FantasyTeam.name,
        Utilisateur.nom_utilisateur.label("username"),
        func.coalesce(func.sum(FantasyTeamScore.total_score), 0).label("total_score"),
        func.count(FantasyTeamScore.id).label("games_played")
    ).join(
        Utilisateur, FantasyTeam.owner_id == Utilisateur.id
    ).outerjoin(
        FantasyTeamScore, FantasyTeam.id == FantasyTeamScore.fantasy_team_id
    ).filter(
        FantasyTeam.league_id == solo_league.id
    ).group_by(
        FantasyTeam.id, FantasyTeam.name, Utilisateur.nom_utilisateur
    ).order_by(
        desc("total_score")
    ).all()
    
    # Calculer les scores des 7 derniers jours
    seven_days_ago = datetime.now().date() - timedelta(days=7)
    
    leaderboard = []
    for rank, team in enumerate(teams_query, start=1):
        # Score des 7 derniers jours
        last_7_days = db.query(
            func.coalesce(func.sum(FantasyTeamScore.total_score), 0)
        ).filter(
            FantasyTeamScore.fantasy_team_id == team.id,
            FantasyTeamScore.score_date >= seven_days_ago
        ).scalar() or 0.0
        
        # Score moyen
        average_score = float(team.total_score) / team.games_played if team.games_played > 0 else 0.0
        
        # Tendance simple (à améliorer avec vraie logique)
        trend = "stable"
        if team.games_played >= 7:
            # Comparer score des 7 derniers jours vs moyenne générale
            if last_7_days / 7 > average_score * 1.1:
                trend = "up"
            elif last_7_days / 7 < average_score * 0.9:
                trend = "down"
        
        leaderboard.append({
            "rank": rank,
            "team_id": team.id,
            "team_name": team.name,
            "owner_username": team.username,
            "total_score": float(team.total_score),
            "last_7_days_score": float(last_7_days),
            "games_played": team.games_played,
            "average_score": round(average_score, 1),
            "trend": trend
        })
    
    return leaderboard


@router.delete("/{league_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_league(
    league_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Supprimer une ligue
    
    **Endpoint :** DELETE /api/v1/leagues/{league_id}
    
    **Authentification requise :** Oui (doit être le commissaire)
    
    **Règles métier :**
    - Seul le commissaire peut supprimer une ligue PRIVATE
    - Les ligues SOLO ne peuvent pas être supprimées
    - Supprime aussi toutes les équipes de la ligue (CASCADE)
    """
    
    league = db.query(League).filter(League.id == league_id).first()
    
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ligue avec ID {league_id} introuvable"
        )
    
    # Vérifications
    if league.type == LeagueType.SOLO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les ligues SOLO ne peuvent pas être supprimées"
        )
    
    if league.commissioner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul le commissaire peut supprimer cette ligue"
        )
    
    db.delete(league)
    db.commit()
    
    return None  # 204 No Content (pas de body)

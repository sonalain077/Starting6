"""
Endpoints API pour gérer les équipes fantasy (FantasyTeam)

Routes disponibles:
- POST   /teams         : Créer une équipe dans une ligue
- GET    /teams/me      : Lister mes équipes
- GET    /teams/{id}    : Détails d'une équipe
- PATCH  /teams/{id}    : Modifier le nom de mon équipe
- DELETE /teams/{id}    : Supprimer mon équipe
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.utilisateur import Utilisateur
from app.models.fantasy_team import FantasyTeam
from app.models.league import League, LeagueType
from app.schemas.fantasy_team import (
    FantasyTeamCreate,
    FantasyTeamRead,
    FantasyTeamUpdate,
    FantasyTeamWithLeague,
    FantasyTeamList
)

router = APIRouter()


# ========================================
# POST /teams - Créer une équipe
# ========================================

@router.post("/", response_model=FantasyTeamRead, status_code=201)
def create_fantasy_team(
    team_data: FantasyTeamCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    ## Créer une nouvelle équipe fantasy dans une ligue
    
    **Requiert une authentification JWT.**
    
    **Exemple de requête :**
    ```json
    {
        "name": "Les Warriors du 77",
        "league_id": 1
    }
    ```
    
    **Règles métier :**
    - Un utilisateur ne peut avoir qu'**une seule équipe par ligue**
    - La ligue doit exister et être active
    - Pour les PRIVATE leagues : max_teams ne doit pas être dépassé
    - Le salary_cap_used commence à 0
    - La waiver_priority est attribuée automatiquement (dernier arrivé)
    """
    
    # 1. Vérifier que la ligue existe et est active
    league = db.query(League).filter(League.id == team_data.league_id).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ligue {team_data.league_id} introuvable"
        )
    
    if not league.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette ligue n'est plus active"
        )
    
    # 2. Vérifier que l'utilisateur n'a pas déjà une équipe dans cette ligue
    existing_team = db.query(FantasyTeam).filter(
        FantasyTeam.owner_id == current_user.id,
        FantasyTeam.league_id == team_data.league_id
    ).first()
    
    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vous avez déjà une équipe dans cette ligue : '{existing_team.name}'"
        )
    
    # 3. Pour les PRIVATE leagues : vérifier max_teams
    if league.type == LeagueType.PRIVATE and league.max_teams:
        teams_count = db.query(FantasyTeam).filter(
            FantasyTeam.league_id == team_data.league_id
        ).count()
        
        if teams_count >= league.max_teams:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cette ligue est complète ({league.max_teams} équipes max)"
            )
    
    # 4. Calculer la waiver_priority (dernier arrivé = priorité la plus basse)
    waiver_priority = None
    if league.type == LeagueType.PRIVATE:
        max_priority = db.query(FantasyTeam).filter(
            FantasyTeam.league_id == team_data.league_id
        ).count()
        waiver_priority = max_priority + 1
    
    # 5. Créer l'équipe
    new_team = FantasyTeam(
        name=team_data.name,
        owner_id=current_user.id,
        league_id=team_data.league_id,
        salary_cap_used=0.0,  # Commence à 0
        waiver_priority=waiver_priority
    )
    
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    
    return new_team


# ========================================
# GET /teams/me - Mes équipes
# ========================================

@router.get("/me", response_model=List[FantasyTeamWithLeague])
def get_my_teams(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    ## Récupérer toutes mes équipes
    
    **Requiert une authentification JWT.**
    
    Retourne la liste de toutes les équipes de l'utilisateur connecté,
    avec les informations de la ligue associée.
    """
    
    teams = db.query(FantasyTeam).filter(
        FantasyTeam.owner_id == current_user.id
    ).all()
    
    # Enrichir avec les infos de la ligue
    teams_with_league = []
    for team in teams:
        team_dict = {
            "id": team.id,
            "name": team.name,
            "owner_id": team.owner_id,
            "league_id": team.league_id,
            "salary_cap_used": team.salary_cap_used,
            "waiver_priority": team.waiver_priority,
            "date_creation": team.date_creation,
            "league_name": team.league.name,
            "league_type": team.league.type.value
        }
        teams_with_league.append(team_dict)
    
    return teams_with_league


# ========================================
# GET /teams/{id} - Détails d'une équipe
# ========================================

@router.get("/{team_id}", response_model=FantasyTeamRead)
def get_team_details(
    team_id: int,
    db: Session = Depends(get_db)
):
    """
    ## Récupérer les détails d'une équipe
    
    **Endpoint public** (pas d'authentification requise).
    
    Retourne les informations détaillées d'une équipe.
    """
    
    team = db.query(FantasyTeam).filter(FantasyTeam.id == team_id).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Équipe {team_id} introuvable"
        )
    
    return team


# ========================================
# PATCH /teams/{id} - Modifier une équipe
# ========================================

@router.patch("/{team_id}", response_model=FantasyTeamRead)
def update_team(
    team_id: int,
    team_data: FantasyTeamUpdate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    ## Modifier le nom de son équipe
    
    **Requiert une authentification JWT.**
    
    Seul le propriétaire de l'équipe peut modifier son nom.
    
    **Exemple de requête :**
    ```json
    {
        "name": "Nouveau nom d'équipe"
    }
    ```
    """
    
    # Récupérer l'équipe
    team = db.query(FantasyTeam).filter(FantasyTeam.id == team_id).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Équipe {team_id} introuvable"
        )
    
    # Vérifier que c'est bien le propriétaire
    if team.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas le propriétaire de cette équipe"
        )
    
    # Mettre à jour le nom si fourni
    if team_data.name is not None:
        team.name = team_data.name
    
    db.commit()
    db.refresh(team)
    
    return team


# ========================================
# DELETE /teams/{id} - Supprimer une équipe
# ========================================

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    ## Supprimer son équipe
    
    **Requiert une authentification JWT.**
    
    Seul le propriétaire de l'équipe peut la supprimer.
    
    ⚠️ **Attention :** Suppression définitive !
    """
    
    # Récupérer l'équipe
    team = db.query(FantasyTeam).filter(FantasyTeam.id == team_id).first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Équipe {team_id} introuvable"
        )
    
    # Vérifier que c'est bien le propriétaire
    if team.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas le propriétaire de cette équipe"
        )
    
    # Supprimer l'équipe
    db.delete(team)
    db.commit()
    
    return None

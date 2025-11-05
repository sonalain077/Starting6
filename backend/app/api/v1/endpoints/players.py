"""
Endpoints API pour les joueurs NBA (Players)

Ces endpoints permettent de :
- Lister les joueurs disponibles avec filtres avancés
- Rechercher par nom, position, équipe
- Obtenir les détails d'un joueur

URL de base : /api/v1/players
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from app.core.database import get_db
from app.models.player import Player, Position
from app.schemas.player import PlayerRead, PlayerDetail, PlayerList

router = APIRouter()


# ========================================
# GET /players - Lister les joueurs avec filtres
# ========================================

@router.get("/", response_model=PlayerList)
def get_players(
    skip: int = Query(0, ge=0, description="Nombre de résultats à sauter"),
    limit: int = Query(20, ge=1, le=100, description="Nombre de résultats max"),
    position: Optional[Position] = Query(None, description="Filtrer par poste"),
    team: Optional[str] = Query(None, max_length=3, description="Code équipe NBA"),
    min_salary: Optional[float] = Query(None, ge=2_000_000, description="Salaire min"),
    max_salary: Optional[float] = Query(None, le=18_000_000, description="Salaire max"),
    search: Optional[str] = Query(None, min_length=2, description="Recherche par nom"),
    is_active: Optional[bool] = Query(True, description="Joueurs actifs uniquement"),
    sort_by: str = Query("fantasy_cost", description="Trier par (fantasy_cost, avg_fantasy_score_last_15, last_name)"),
    sort_order: str = Query("desc", description="Ordre (asc, desc)"),
    db: Session = Depends(get_db)
):
    """
    📋 Liste tous les joueurs NBA disponibles
    
    **Filtres disponibles :**
    - `position` : PG, SG, SF, PF, C
    - `team` : Code NBA (ex: LAL, BOS, MIA)
    - `min_salary` / `max_salary` : Fourchette de salaire
    - `search` : Recherche par nom (prénom ou nom)
    - `is_active` : Exclure les blessés/inactifs
    
    **Tri :**
    - `sort_by` : fantasy_cost (défaut), avg_fantasy_score_last_15, last_name
    - `sort_order` : desc (défaut) ou asc
    
    **Pagination :**
    - `skip` : Offset (défaut: 0)
    - `limit` : Max 100 résultats (défaut: 20)
    
    **Exemple :**
    ```
    GET /players?position=PG&min_salary=5000000&sort_by=fantasy_cost&limit=10
    ```
    """
    # Construction de la requête de base
    query = db.query(Player)
    
    # Dictionnaire pour tracker les filtres appliqués
    filters_applied = {}
    
    # Filtre par activité (par défaut: actifs uniquement)
    if is_active is not None:
        query = query.filter(Player.is_active == is_active)
        filters_applied["is_active"] = is_active
    
    # Filtre par position
    if position:
        query = query.filter(Player.position == position)
        filters_applied["position"] = position.value
    
    # Filtre par équipe
    if team:
        team_upper = team.upper()
        query = query.filter(Player.team == team_upper)
        filters_applied["team"] = team_upper
    
    # Filtre par salaire (fourchette)
    if min_salary:
        query = query.filter(Player.fantasy_cost >= min_salary)
        filters_applied["min_salary"] = min_salary
    
    if max_salary:
        query = query.filter(Player.fantasy_cost <= max_salary)
        filters_applied["max_salary"] = max_salary
    
    # Recherche par nom (insensible à la casse)
    if search:
        search_pattern = f"%{search.lower()}%"
        query = query.filter(
            or_(
                Player.first_name.ilike(search_pattern),
                Player.last_name.ilike(search_pattern)
            )
        )
        filters_applied["search"] = search
    
    # Comptage total AVANT pagination
    total = query.count()
    
    # Tri
    valid_sort_fields = {
        "fantasy_cost": Player.fantasy_cost,
        "avg_fantasy_score_last_15": Player.avg_fantasy_score_last_15,
        "last_name": Player.last_name
    }
    
    if sort_by not in valid_sort_fields:
        sort_by = "fantasy_cost"
    
    sort_column = valid_sort_fields[sort_by]
    
    if sort_order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Pagination
    players = query.offset(skip).limit(limit).all()
    
    return PlayerList(
        players=players,
        total=total,
        skip=skip,
        limit=limit,
        filters_applied=filters_applied
    )


# ========================================
# GET /players/{player_id} - Détails d'un joueur
# ========================================

@router.get("/{player_id}", response_model=PlayerDetail)
def get_player(
    player_id: int,
    db: Session = Depends(get_db)
):
    """
    🔍 Récupère les détails complets d'un joueur
    
    Retourne toutes les statistiques du joueur :
    - Informations de base (nom, poste, équipe)
    - Salaire fantasy actuel
    - Moyenne des 15 derniers matchs
    - Écart-type (consistance)
    - Matchs joués sur 20 jours
    
    **Exemple :**
    ```
    GET /players/123
    ```
    """
    player = db.query(Player).filter(Player.id == player_id).first()
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Joueur avec l'ID {player_id} introuvable"
        )
    
    return player

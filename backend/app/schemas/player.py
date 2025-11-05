"""
Schémas Pydantic pour les joueurs NBA (Player)

Ces schémas définissent la structure des données pour:
- Lister les joueurs disponibles
- Filtrer par position, équipe, salaire
- Afficher les détails d'un joueur
"""
from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional
from datetime import datetime
from app.models.player import Position


# ========================================
# SCHÉMAS DE BASE
# ========================================

class PlayerBase(BaseModel):
    """
    Schéma de base pour un joueur NBA
    Contient les informations essentielles
    """
    first_name: str
    last_name: str
    position: Position
    team: str = Field(description="Code NBA de l'équipe (ex: LAL, BOS)")
    fantasy_cost: float = Field(description="Salaire fantasy (2M$-18M$)")


# ========================================
# SCHÉMA DE LECTURE SIMPLE
# ========================================

class PlayerRead(PlayerBase):
    """
    Schéma pour lire un joueur
    Utilisé dans les listes et recherches
    """
    id: int
    external_api_id: int
    is_active: bool = Field(description="False si blessé/inactif")
    avg_fantasy_score_last_15: Optional[float] = Field(
        default=None,
        description="Moyenne des 15 derniers matchs"
    )
    games_played_last_20: Optional[int] = Field(
        default=None,
        description="Matchs joués sur 20 jours"
    )
    
    @computed_field
    @property
    def full_name(self) -> str:
        """Nom complet du joueur"""
        return f"{self.first_name} {self.last_name}"
    
    model_config = ConfigDict(from_attributes=True)


# ========================================
# SCHÉMA DE LECTURE DÉTAILLÉE
# ========================================

class PlayerDetail(PlayerRead):
    """
    Schéma avec statistiques complètes
    Utilisé pour GET /players/{id}
    """
    avg_fantasy_score_last_15: Optional[float] = Field(
        default=None,
        description="Moyenne des 15 derniers matchs"
    )
    games_played_last_20: Optional[int] = Field(
        default=None,
        description="Matchs joués sur 20 derniers jours"
    )
    date_creation: datetime
    last_updated: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ========================================
# SCHÉMA DE LISTE AVEC PAGINATION
# ========================================

class PlayerList(BaseModel):
    """
    Schéma pour lister les joueurs avec pagination et filtres
    """
    players: list[PlayerRead]
    total: int
    skip: int
    limit: int
    filters_applied: dict = Field(
        default_factory=dict,
        description="Filtres appliqués (position, team, etc.)"
    )

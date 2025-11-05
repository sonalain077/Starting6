"""
Schémas Pydantic pour les équipes fantasy (FantasyTeam)

Ces schémas définissent la structure des données pour:
- Créer une équipe dans une ligue
- Lire les informations d'une équipe
- Lister les équipes d'un utilisateur
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# ========================================
# SCHÉMAS DE BASE
# ========================================

class FantasyTeamBase(BaseModel):
    """
    Schéma de base pour une équipe fantasy
    Contient les champs communs à tous les schémas
    """
    name: str = Field(
        ..., 
        min_length=3, 
        max_length=50,
        description="Nom de l'équipe (3-50 caractères)"
    )


# ========================================
# SCHÉMA DE CRÉATION
# ========================================

class FantasyTeamCreate(FantasyTeamBase):
    """
    Schéma pour créer une nouvelle équipe dans une ligue
    
    Usage:
        POST /teams
        {
            "name": "Les Warriors du 77",
            "league_id": 1
        }
    
    Règles métier:
    - Un utilisateur ne peut avoir qu'une seule équipe par ligue
    - Le salary_cap_used commence à 0
    - La waiver_priority est attribuée automatiquement
    """
    league_id: int = Field(
        ..., 
        gt=0,
        description="ID de la ligue à rejoindre"
    )


# ========================================
# SCHÉMA DE LECTURE
# ========================================

class FantasyTeamRead(FantasyTeamBase):
    """
    Schéma pour lire les informations d'une équipe
    Retourné par les endpoints GET
    """
    id: int
    owner_id: int
    league_id: int
    salary_cap_used: float = Field(
        description="Montant utilisé du salary cap (max 60M$)"
    )
    waiver_priority: Optional[int] = Field(
        default=None,
        description="Position dans l'ordre des waivers (PRIVATE league uniquement)"
    )
    date_creation: datetime
    
    # Configuration Pydantic v2
    model_config = ConfigDict(from_attributes=True)


# ========================================
# SCHÉMA DE MISE À JOUR
# ========================================

class FantasyTeamUpdate(BaseModel):
    """
    Schéma pour mettre à jour une équipe
    Seul le nom peut être modifié par l'utilisateur
    """
    name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="Nouveau nom de l'équipe"
    )


# ========================================
# SCHÉMAS ÉTENDUS (avec relations)
# ========================================

class FantasyTeamWithLeague(FantasyTeamRead):
    """
    Équipe avec informations de la ligue
    Utile pour afficher "Mes Équipes"
    """
    league_name: str = Field(description="Nom de la ligue")
    league_type: str = Field(description="Type de ligue (SOLO/PRIVATE)")
    
    model_config = ConfigDict(from_attributes=True)


class FantasyTeamList(BaseModel):
    """
    Schéma pour lister les équipes avec pagination
    """
    teams: list[FantasyTeamRead]
    total: int
    skip: int
    limit: int

"""
Schémas Pydantic pour la gestion du roster (6 joueurs d'une équipe)

Ces schémas permettent de :
- Afficher le roster complet avec salary cap
- Ajouter un joueur avec validation (cap + poste)
- Retirer un joueur
- Lister les joueurs disponibles selon le budget restant
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime

from app.models.fantasy_team_player import RosterSlot
from app.schemas.player import PlayerRead


# ========================================
# SCHÉMAS DE LECTURE DU ROSTER
# ========================================

class RosterSlotRead(BaseModel):
    """
    Un slot du roster (une des 6 positions)
    
    Contient :
    - La position (PG, SG, SF, PF, C, UTIL)
    - Le joueur assigné (ou None si vide)
    - Le salaire "gelé" au moment de l'acquisition
    - La date d'acquisition
    """
    position_slot: RosterSlot
    player: Optional[PlayerRead] = None
    acquired_salary: Optional[float] = Field(
        None,
        description="Salaire gelé au moment de l'achat (immutable)"
    )
    date_acquired: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class RosterRead(BaseModel):
    """
    Roster complet d'une équipe avec salary cap
    
    Affiche :
    - Les 6 positions avec joueurs assignés
    - Le salary cap utilisé (somme des acquired_salary)
    - Le salary cap restant (60M$ - utilisé)
    - Le nombre de transferts cette semaine
    """
    team_id: int
    team_name: str
    roster: List[RosterSlotRead] = Field(
        description="Les 6 positions (PG, SG, SF, PF, C, UTIL)"
    )
    salary_cap_used: float = Field(
        description="Montant total utilisé du salary cap"
    )
    salary_cap_remaining: float = Field(
        description="Budget restant (60M$ - utilisé)"
    )
    transfers_this_week: int = Field(
        description="Nombre de transferts effectués cette semaine (max 2)"
    )
    is_roster_complete: bool = Field(
        description="True si 6/6 joueurs (équipe active), False si en construction"
    )
    roster_status: str = Field(
        description="'CONSTRUCTION' (transferts illimités) ou 'ACTIVE' (limite 2/semaine)"
    )
    
    model_config = ConfigDict(from_attributes=True)


# ========================================
# SCHÉMAS POUR AJOUTER UN JOUEUR
# ========================================

class AddPlayerToRoster(BaseModel):
    """
    Requête pour ajouter un joueur au roster
    
    Validations automatiques :
    - Le joueur existe
    - Le poste est disponible (ou UTIL libre)
    - Le salary cap est respecté (60M$ max)
    - Pas de cooldown actif sur ce joueur
    - Moins de 2 transferts cette semaine
    """
    player_id: int = Field(description="ID du joueur à ajouter")
    position_slot: RosterSlot = Field(
        description="Position assignée (PG, SG, SF, PF, C, UTIL)"
    )
    
    @field_validator('position_slot')
    def validate_position_slot(cls, v):
        """Vérifie que la position est valide"""
        valid_positions = ['PG', 'SG', 'SF', 'PF', 'C', 'UTIL']
        if v.value not in valid_positions:
            raise ValueError(f"Position invalide. Doit être : {', '.join(valid_positions)}")
        return v


class AddPlayerResponse(BaseModel):
    """
    Réponse après ajout d'un joueur
    
    Confirme :
    - Le joueur ajouté
    - La position assignée
    - Le nouveau salary cap utilisé
    - Le budget restant
    """
    message: str
    player_added: PlayerRead
    position_slot: RosterSlot
    salary_cap_used: float
    salary_cap_remaining: float
    transfers_remaining_this_week: int
    
    model_config = ConfigDict(from_attributes=True)


# ========================================
# SCHÉMAS POUR LISTER LES JOUEURS DISPONIBLES
# ========================================

class AvailablePlayerRead(BaseModel):
    """
    Un joueur disponible à l'achat
    
    Affiche :
    - Toutes les infos du joueur
    - Si le joueur est compatible avec le budget restant
    - Si le joueur a un cooldown actif (viré récemment)
    """
    player: PlayerRead
    is_affordable: bool = Field(
        description="True si le salaire <= budget restant"
    )
    has_cooldown: bool = Field(
        description="True si viré dans les 7 derniers jours"
    )
    cooldown_ends: Optional[datetime] = Field(
        None,
        description="Date de fin du cooldown (si applicable)"
    )
    
    model_config = ConfigDict(from_attributes=True)


class AvailablePlayersResponse(BaseModel):
    """
    Liste des joueurs disponibles avec filtres
    
    Permet de filtrer par :
    - Position (PG, SG, SF, PF, C)
    - Équipe NBA
    - Budget max (salary_cap_remaining)
    - Recherche par nom
    """
    team_id: int
    salary_cap_remaining: float
    available_positions: List[str] = Field(
        description="Positions encore libres dans le roster"
    )
    players: List[AvailablePlayerRead]
    total_count: int
    
    model_config = ConfigDict(from_attributes=True)

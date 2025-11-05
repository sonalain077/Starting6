"""
Schemas Pydantic pour League (Ligue)

Ces schemas définissent le format des données échangées via l'API.
Pydantic valide automatiquement les données entrantes et sortantes.

Différence avec les modèles SQLAlchemy :
- Modèles SQLAlchemy (models/league.py) = structure en base de données
- Schemas Pydantic (schemas/league.py) = structure en JSON pour l'API
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class LeagueTypeEnum(str, Enum):
    """
    Type de ligue (SOLO ou PRIVATE)
    
    Correspond au LeagueType de SQLAlchemy mais pour Pydantic.
    """
    SOLO = "SOLO"
    PRIVATE = "PRIVATE"


class LeagueBase(BaseModel):
    """
    Schema de base pour League
    
    Contient les champs communs à tous les schemas League.
    Ces champs peuvent être fournis par l'utilisateur.
    """
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nom de la ligue",
        examples=["NBA Fantasy 2025", "Ligue entre potes"]
    )
    # ... = obligatoire
    # min_length=3 = minimum 3 caractères
    # max_length=100 = maximum 100 caractères
    
    type: LeagueTypeEnum = Field(
        default=LeagueTypeEnum.SOLO,
        description="Type de ligue (SOLO ou PRIVATE)"
    )
    
    max_teams: Optional[int] = Field(
        default=None,
        ge=8,
        le=12,
        description="Nombre maximum d'équipes (8-12 pour PRIVATE, illimité pour SOLO)"
    )
    # Optional = peut être None
    # ge=8 = greater or equal (>= 8)
    # le=12 = less or equal (<= 12)
    
    salary_cap: int = Field(
        default=60_000_000,
        ge=1_000_000,
        le=100_000_000,
        description="Plafond salarial en dollars (60M$ par défaut)"
    )


class LeagueCreate(BaseModel):
    """
    Schema pour créer une ligue PRIVATE (requête POST)
    
    ⚠️ IMPORTANT : Seules les ligues PRIVATE peuvent être créées via l'API.
    La ligue SOLO est unique et globale, créée automatiquement au démarrage.
    
    Exemple d'utilisation :
    POST /api/v1/leagues
    Body:
    {
        "name": "Ma Ligue Privée",
        "max_teams": 10,
        "salary_cap": 60000000
    }
    
    Note : Le champ "type" n'est pas demandé car c'est toujours PRIVATE.
    """
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nom de la ligue",
        examples=["Ligue entre potes", "Champions League 2025"]
    )
    
    max_teams: int = Field(
        ...,
        ge=8,
        le=12,
        description="Nombre maximum d'équipes (8-12 obligatoire pour PRIVATE)"
    )
    # Obligatoire pour PRIVATE (pas Optional)
    
    salary_cap: int = Field(
        default=60_000_000,
        ge=1_000_000,
        le=100_000_000,
        description="Plafond salarial en dollars (60M$ par défaut)"
    )


class LeagueRead(LeagueBase):
    """
    Schema pour lire une ligue (réponse GET)
    
    Contient tous les champs de LeagueBase + les champs générés par la BDD.
    
    Exemple de réponse :
    GET /api/v1/leagues/1
    Response:
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
    """
    # Champs supplémentaires générés par la base de données
    id: int
    commissioner_id: Optional[int] = None
    is_active: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    date_creation: datetime
    
    # Configuration Pydantic v2
    model_config = ConfigDict(
        from_attributes=True  # Permet de créer le schema depuis un objet SQLAlchemy
    )
    # from_attributes=True permet de faire :
    # league_db = db.query(League).first()  # Objet SQLAlchemy
    # league_response = LeagueRead.from_orm(league_db)  # Conversion auto en JSON


class LeagueUpdate(BaseModel):
    """
    Schema pour modifier une ligue (requête PATCH/PUT)
    
    Tous les champs sont optionnels (on peut modifier juste le nom, ou juste le max_teams, etc.)
    
    Exemple :
    PATCH /api/v1/leagues/1
    Body:
    {
        "name": "Nouveau nom",
        "is_active": false
    }
    """
    name: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=100
    )
    max_teams: Optional[int] = Field(
        default=None,
        ge=8,
        le=12
    )
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class LeagueList(BaseModel):
    """
    Schema pour lister plusieurs ligues
    
    Utile pour la pagination.
    
    Exemple :
    GET /api/v1/leagues?skip=0&limit=10
    Response:
    {
        "total": 25,
        "leagues": [
            {...},
            {...},
            ...
        ]
    }
    """
    total: int = Field(description="Nombre total de ligues")
    leagues: list[LeagueRead] = Field(description="Liste des ligues")

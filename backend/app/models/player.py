"""
Modèle SQLAlchemy pour la table Player (Joueur NBA)

Représente un joueur de la NBA avec ses statistiques fantasy.
Les données sont synchronisées avec l'API balldontlie.io
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class Position(enum.Enum):
    """
    Postes de basketball (5 postes traditionnels)
    
    PG = Point Guard (Meneur)
    SG = Shooting Guard (Arrière)
    SF = Small Forward (Ailier)
    PF = Power Forward (Ailier Fort)
    C = Center (Pivot)
    """
    PG = "PG"  # Point Guard (Meneur)
    SG = "SG"  # Shooting Guard (Arrière)
    SF = "SF"  # Small Forward (Ailier)
    PF = "PF"  # Power Forward (Ailier Fort)
    C = "C"    # Center (Pivot)


class Player(Base):
    """
    Modèle Player - Représente un joueur de la NBA
    
    Attributs:
        id: ID interne de notre base de données
        external_api_id: ID du joueur dans l'API balldontlie.io
        first_name: Prénom du joueur
        last_name: Nom de famille du joueur
        full_name: Nom complet (pour faciliter les recherches)
        position: Poste du joueur (PG, SG, SF, PF, C)
        team: Équipe NBA actuelle (ex: "Lakers", "Warriors")
        team_abbreviation: Code de l'équipe (ex: "LAL", "GSW")
        jersey_number: Numéro de maillot
        height: Taille en pouces (inches)
        weight: Poids en livres (pounds)
        fantasy_cost: Coût fantasy actuel (salaire dynamique)
        avg_fantasy_score_last_15: Moyenne des scores fantasy sur les 15 derniers matchs
        games_played_last_20: Nombre de matchs joués dans les 20 derniers jours
        is_injured: Le joueur est-il blessé?
        injury_status: Détails sur la blessure (si applicable)
        is_active: Le joueur est-il actif dans la NBA?
        last_updated: Dernière mise à jour des données
    
    Relations:
        game_scores: Tous les scores de ce joueur par match
        fantasy_team_players: Équipes fantasy qui ont ce joueur
    """
    
    __tablename__ = "players"
    
    # === COLONNES ===
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    
    # ID de l'API externe (balldontlie.io)
    external_api_id = Column(
        Integer,
        unique=True,
        nullable=False,
        index=True
    )
    # On stocke cet ID pour synchroniser avec l'API
    
    # === INFORMATIONS PERSONNELLES ===
    
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    
    # Nom complet pour faciliter les recherches
    full_name = Column(
        String(100),
        nullable=False,
        index=True
    )
    # Exemple: "LeBron James", "Stephen Curry"
    
    # === INFORMATIONS DE JEU ===
    
    # Poste du joueur
    position = Column(
        "player_position",  # Nom de la colonne en BDD (évite le conflit avec mot réservé "position")
        SQLEnum(Position, name="player_position_enum"),  # Nom du type ENUM en SQL
        nullable=False,
        index=True
    )
    
    # Équipe NBA actuelle
    team = Column(String(50), nullable=True)
    # Exemple: "Los Angeles Lakers"
    
    team_abbreviation = Column(String(3), nullable=True, index=True)
    # Exemple: "LAL", "GSW", "BOS"
    
    jersey_number = Column(String(3), nullable=True)
    # Exemple: "23", "30", "11"
    
    # === INFORMATIONS PHYSIQUES ===
    
    height = Column(Integer, nullable=True)
    # En pouces (inches) - Exemple: 81 inches = 6'9"
    
    weight = Column(Integer, nullable=True)
    # En livres (pounds) - Exemple: 250 lbs
    
    # === STATISTIQUES FANTASY ===
    
    # Coût fantasy actuel (salaire dynamique)
    fantasy_cost = Column(
        Integer,
        nullable=False,
        default=5_000_000,  # 5M$ par défaut
        index=True
    )
    # Min: 2M$, Max: 18M$ selon la formule de calcul
    
    # Moyenne des scores fantasy sur les 15 derniers matchs
    avg_fantasy_score_last_15 = Column(
        Float,
        nullable=True,
        default=0.0
    )
    
    # Nombre de matchs joués dans les 20 derniers jours
    games_played_last_20 = Column(
        Integer,
        nullable=False,
        default=0
    )
    # Utilisé pour calculer le facteur de disponibilité
    
    # === STATUT DU JOUEUR ===
    
    # Est-il blessé?
    is_injured = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True
    )
    
    # Détails sur la blessure
    injury_status = Column(String(200), nullable=True)
    # Exemple: "Out - Knee injury", "Day-to-Day - Ankle"
    
    # Est-il actif dans la NBA?
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True
    )
    # False si retraité ou agent libre
    
    # === MÉTADONNÉES ===
    
    # Date de dernière mise à jour
    last_updated = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    date_creation = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # === RELATIONS ===
    
    # Scores de ce joueur par match
    game_scores = relationship(
        "PlayerGameScore",
        back_populates="player",
        cascade="all, delete-orphan"
    )
    
    # Équipes fantasy qui ont ce joueur
    fantasy_team_players = relationship(
        "FantasyTeamPlayer",
        back_populates="player",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Player(id={self.id}, name='{self.full_name}', pos={self.position.value}, cost=${self.fantasy_cost:,})>"

"""
Modèle SQLAlchemy pour la table FantasyTeamPlayer (Table d'Association)

Table intermédiaire entre FantasyTeam et Player.
Permet de savoir quel joueur occupe quel poste dans quelle équipe.

Exemple:
- Team "Les Monstars" a LeBron James au poste UTIL
- Team "Dream Squad" a Stephen Curry au poste PG
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class RosterSlot(enum.Enum):
    """
    Postes dans le roster d'une équipe fantasy (Starting Six)
    
    Une équipe DOIT avoir:
    - 1 PG (Point Guard / Meneur)
    - 1 SG (Shooting Guard / Arrière)
    - 1 SF (Small Forward / Ailier)
    - 1 PF (Power Forward / Ailier Fort)
    - 1 C (Center / Pivot)
    - 1 UTIL (Utility / Sixième homme - n'importe quel poste)
    """
    PG = "PG"
    SG = "SG"
    SF = "SF"
    PF = "PF"
    C = "C"
    UTIL = "UTIL"  # Sixième homme (n'importe quel poste)


class FantasyTeamPlayer(Base):
    """
    Modèle FantasyTeamPlayer - Association entre une équipe et un joueur
    
    Cette table dit:
    - Quelle équipe fantasy a quel joueur NBA
    - À quel poste ce joueur est placé dans l'équipe
    - Depuis quand il est dans l'équipe
    - Quel était son salaire au moment de l'acquisition
    
    Attributs:
        id: Identifiant unique
        fantasy_team_id: ID de l'équipe fantasy
        player_id: ID du joueur NBA
        roster_slot: Poste occupé (PG, SG, SF, PF, C, UTIL)
        salary_at_acquisition: Salaire du joueur au moment de l'acquisition
        date_acquired: Date d'acquisition du joueur
    
    Relations:
        fantasy_team: Équipe fantasy
        player: Joueur NBA
    
    Contraintes:
        - Une équipe ne peut avoir qu'un seul joueur par poste
        - Une équipe ne peut avoir le même joueur deux fois
    """
    
    __tablename__ = "fantasy_team_players"
    
    # === COLONNES ===
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    
    # ID de l'équipe fantasy
    fantasy_team_id = Column(
        Integer,
        ForeignKey("fantasy_teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # ID du joueur NBA
    player_id = Column(
        Integer,
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Poste occupé dans l'équipe
    roster_slot = Column(
        SQLEnum(RosterSlot),
        nullable=False
    )
    # Exemple: "PG", "SG", "UTIL"
    
    # Salaire du joueur au moment de l'acquisition
    salary_at_acquisition = Column(
        Integer,
        nullable=False
    )
    # On stocke le salaire historique pour voir l'évolution
    # Exemple: Si on a pris LeBron à 12M$ et qu'il monte à 15M$,
    # on sait qu'on a fait une bonne affaire!
    
    # Date d'acquisition
    date_acquired = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # === RELATIONS ===
    
    # Équipe fantasy
    fantasy_team = relationship(
        "FantasyTeam",
        back_populates="players"
    )
    
    # Joueur NBA
    player = relationship(
        "Player",
        back_populates="fantasy_team_players"
    )
    
    # === CONTRAINTES ===
    
    __table_args__ = (
        # Une équipe ne peut avoir qu'un seul joueur par poste
        UniqueConstraint('fantasy_team_id', 'roster_slot', name='uq_team_slot'),
        # Une équipe ne peut avoir le même joueur deux fois
        # (sauf en SOLO league où plusieurs équipes peuvent avoir le même joueur)
        # Note: Cette contrainte sera gérée au niveau applicatif pour PRIVATE leagues
    )
    
    def __repr__(self):
        return f"<FantasyTeamPlayer(team_id={self.fantasy_team_id}, player_id={self.player_id}, slot={self.roster_slot.value})>"

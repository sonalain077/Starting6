"""
Modèle SQLAlchemy pour la table Transfer

Historique de tous les transferts (ajouts/suppressions de joueurs).
Permet de tracer qui a fait quoi et quand, et d'appliquer les règles:
- Maximum 2 transferts par semaine
- Cooldown de 7 jours après avoir viré un joueur
- Attribution selon le système (premier arrivé pour SOLO, waiver pour PRIVATE)
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class TransferType(enum.Enum):
    """
    Types de transferts possibles
    
    ADD: Ajout d'un joueur à l'équipe
    DROP: Retrait d'un joueur de l'équipe
    TRADE: Échange entre deux équipes (pas implémenté en Phase 2)
    """
    ADD = "ADD"
    DROP = "DROP"
    TRADE = "TRADE"


class TransferStatus(enum.Enum):
    """
    Statut d'un transfert
    
    PENDING: En attente de traitement (waiver system pour PRIVATE leagues)
    COMPLETED: Transfert effectué
    REJECTED: Transfert refusé (salary cap dépassé, limite atteinte, etc.)
    CANCELLED: Annulé par l'utilisateur
    """
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class Transfer(Base):
    """
    Modèle Transfer - Historique des transferts de joueurs
    
    Chaque ligne représente un transfert (ajout ou suppression).
    Permet de:
    - Tracer l'historique complet des mouvements
    - Appliquer le cooldown de 7 jours
    - Compter les transferts de la semaine
    - Gérer le waiver system (PRIVATE leagues)
    
    Attributs:
        id: Identifiant unique
        fantasy_team_id: ID de l'équipe qui fait le transfert
        player_id: ID du joueur concerné
        transfer_type: Type (ADD, DROP, TRADE)
        status: Statut (PENDING, COMPLETED, REJECTED, CANCELLED)
        roster_slot: Poste occupé/libéré (PG, SG, SF, PF, C, UTIL)
        salary_at_transfer: Salaire du joueur au moment du transfert
        reason: Raison du rejet (si applicable)
        waiver_priority_used: Priorité waiver utilisée (PRIVATE leagues)
        processed_at: Date de traitement du transfert
        date_creation: Date de demande du transfert
    
    Relations:
        fantasy_team: Équipe qui fait le transfert
        player: Joueur concerné
    """
    
    __tablename__ = "transfers"
    
    # === COLONNES ===
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    
    # === IDENTIFICATION ===
    
    fantasy_team_id = Column(
        Integer,
        ForeignKey("fantasy_teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    player_id = Column(
        Integer,
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # === TYPE ET STATUT ===
    
    transfer_type = Column(
        SQLEnum(TransferType),
        nullable=False,
        index=True
    )
    
    status = Column(
        SQLEnum(TransferStatus),
        nullable=False,
        default=TransferStatus.PENDING,
        index=True
    )
    
    # === DÉTAILS DU TRANSFERT ===
    
    roster_slot = Column(
        String(10),
        nullable=True
    )
    # Poste concerné: "PG", "SG", "SF", "PF", "C", "UTIL"
    
    salary_at_transfer = Column(
        Integer,
        nullable=False
    )
    # Salaire du joueur au moment du transfert (historique)
    
    # Raison du rejet (si status = REJECTED)
    reason = Column(
        String(255),
        nullable=True
    )
    # Exemples:
    # - "Salary cap exceeded"
    # - "Transfer limit reached (2/week)"
    # - "Player on cooldown (7 days)"
    # - "Player already owned by another team (PRIVATE league)"
    
    # === WAIVER SYSTEM (PRIVATE LEAGUES) ===
    
    waiver_priority_used = Column(
        Integer,
        nullable=True
    )
    # Priorité waiver au moment du transfert
    # NULL pour SOLO leagues
    
    # === DATES ===
    
    # Date de demande du transfert
    date_creation = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    # Date de traitement (quand status passe à COMPLETED/REJECTED)
    processed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # === RELATIONS ===
    
    fantasy_team = relationship(
        "FantasyTeam",
        back_populates="transfers"
    )
    
    player = relationship("Player")
    
    def __repr__(self):
        return f"<Transfer(id={self.id}, type={self.transfer_type.value}, status={self.status.value}, player_id={self.player_id})>"

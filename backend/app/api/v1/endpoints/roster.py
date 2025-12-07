"""
Endpoints pour la gestion du roster (6 joueurs par équipe)

Routes disponibles :
- GET /teams/{team_id}/roster : Afficher le roster complet
- POST /teams/{team_id}/roster : Ajouter un joueur au roster
- DELETE /teams/{team_id}/roster/{player_id} : Retirer un joueur
- GET /teams/{team_id}/available-players : Lister les joueurs disponibles
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.utilisateur import Utilisateur
from app.models.fantasy_team import FantasyTeam
from app.models.fantasy_team_player import FantasyTeamPlayer, RosterSlot
from app.models.player import Player
from app.models.transfer import Transfer, TransferType, TransferStatus
from app.models.league import League, LeagueType
from app.schemas.roster import (
    RosterRead,
    RosterSlotRead,
    AddPlayerToRoster,
    AddPlayerResponse,
    AvailablePlayerRead,
    AvailablePlayersResponse
)
from app.schemas.player import PlayerRead

router = APIRouter(prefix="/teams", tags=["roster"])

# Constante pour le salary cap
SALARY_CAP_MAX = 60_000_000  # 60 millions
# Mode Solo League : Transferts libres (pas de limite)


# ========================================
# ENDPOINT 1 : GET /teams/{team_id}/roster
# ========================================

@router.get("/{team_id}/roster", response_model=RosterRead)
def get_team_roster(
    team_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📋 Affiche le roster complet d'une équipe (6 positions)
    
    Retourne :
    - Les 6 positions avec joueur assigné ou None
    - Le salary cap utilisé (somme des acquired_salary)
    - Le salary cap restant
    - Le nombre de transferts cette semaine
    
    Positions :
    - PG (Point Guard / Meneur)
    - SG (Shooting Guard / Arrière)
    - SF (Small Forward / Ailier)
    - PF (Power Forward / Ailier Fort)
    - C (Center / Pivot)
    - UTIL (Utility / Sixième Homme - n'importe quel poste)
    """
    
    # 1. Vérifier que l'équipe existe
    team = db.query(FantasyTeam).filter(FantasyTeam.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipe introuvable"
        )
    
    # 2. Vérifier que l'utilisateur est propriétaire de l'équipe
    if team.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas propriétaire de cette équipe"
        )
    
    # 3. Récupérer tous les joueurs du roster
    roster_players = db.query(FantasyTeamPlayer).filter(
        FantasyTeamPlayer.fantasy_team_id == team_id
    ).all()
    
    # 4. Créer un dictionnaire position -> joueur
    roster_dict = {}
    for roster_player in roster_players:
        roster_dict[roster_player.roster_slot.value] = {
            'player': roster_player.player,
            'acquired_salary': roster_player.salary_at_acquisition,
            'date_acquired': roster_player.date_acquired
        }
    
    # 5. Construire les 6 positions (avec ou sans joueur)
    all_positions = ['PG', 'SG', 'SF', 'PF', 'C', 'UTIL']
    roster_slots = []
    
    for position in all_positions:
        if position in roster_dict:
            # Position occupée
            slot_data = roster_dict[position]
            roster_slots.append(RosterSlotRead(
                position_slot=RosterSlot(position),
                player=PlayerRead.model_validate(slot_data['player']),
                acquired_salary=slot_data['acquired_salary'],
                date_acquired=slot_data['date_acquired']
            ))
        else:
            # Position libre
            roster_slots.append(RosterSlotRead(
                position_slot=RosterSlot(position),
                player=None,
                acquired_salary=None,
                date_acquired=None
            ))
    
    # 6. Calculer le salary cap utilisé
    salary_cap_used = team.salary_cap_used or 0.0
    salary_cap_remaining = SALARY_CAP_MAX - salary_cap_used
    
    # 7. Compter les transferts de cette semaine
    # (On compte les transferts depuis le dernier lundi)
    today = datetime.now().date()
    days_since_monday = today.weekday()  # 0 = lundi, 6 = dimanche
    last_monday = today - timedelta(days=days_since_monday)
    
    transfers_this_week = db.query(Transfer).filter(
        and_(
            Transfer.fantasy_team_id == team_id,
            Transfer.status == TransferStatus.COMPLETED,
            Transfer.processed_at >= last_monday
        )
    ).count()
    
    # 8. Déterminer le statut du roster
    is_complete = bool(team.is_roster_complete)
    roster_status = "ACTIVE" if is_complete else "CONSTRUCTION"
    
    # 9. Retourner le roster complet
    return RosterRead(
        team_id=team.id,
        team_name=team.name,
        roster=roster_slots,
        salary_cap_used=salary_cap_used,
        salary_cap_remaining=salary_cap_remaining,
        transfers_this_week=transfers_this_week if is_complete else 0,
        is_roster_complete=is_complete,
        roster_status=roster_status
    )


# ========================================
# ENDPOINT 2 : POST /teams/{team_id}/roster
# ========================================

@router.post("/{team_id}/roster", response_model=AddPlayerResponse, status_code=status.HTTP_201_CREATED)
def add_player_to_roster(
    team_id: int,
    data: AddPlayerToRoster,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ➕ Ajoute un joueur au roster
    
    Validations effectuées :
    1. L'équipe existe et appartient à l'utilisateur
    2. Le joueur existe et est actif
    3. La position demandée est libre
    4. Le salary cap n'est pas dépassé (60M$ max)
    
    Pour UTIL : le joueur peut être de n'importe quel poste
    Pour les autres : le joueur doit avoir le bon poste
    
    Mode Solo League : Transferts libres sans limitation
    """
    
    # 1. Vérifier que l'équipe existe
    team = db.query(FantasyTeam).filter(FantasyTeam.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipe introuvable"
        )
    
    # 2. Vérifier la propriété
    if team.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas propriétaire de cette équipe"
        )
    
    # 3. Vérifier que le joueur existe
    player = db.query(Player).filter(Player.id == data.player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Joueur introuvable"
        )
    
    if not player.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{player.full_name} n'est pas actif dans la NBA"
        )
    
    # 4. Vérifier que la position demandée est libre
    existing_slot = db.query(FantasyTeamPlayer).filter(
        and_(
            FantasyTeamPlayer.fantasy_team_id == team_id,
            FantasyTeamPlayer.roster_slot == data.position_slot
        )
    ).first()
    
    if existing_slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La position {data.position_slot.value} est déjà occupée"
        )
    
    # 5. Vérifier la compatibilité position/joueur (sauf pour UTIL)
    if data.position_slot != RosterSlot.UTIL:
        if player.position.value != data.position_slot.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{player.full_name} est {player.position.value}, pas {data.position_slot.value}. Utilisez la position UTIL pour ce joueur."
            )
    
    # 6. Vérifier que le joueur n'est pas déjà dans le roster
    already_in_roster = db.query(FantasyTeamPlayer).filter(
        and_(
            FantasyTeamPlayer.fantasy_team_id == team_id,
            FantasyTeamPlayer.player_id == data.player_id
        )
    ).first()
    
    if already_in_roster:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{player.full_name} est déjà dans votre roster"
        )
    
    # 7. Vérifier le salary cap
    current_cap = team.salary_cap_used or 0.0
    new_cap = current_cap + player.fantasy_cost
    
    if new_cap > SALARY_CAP_MAX:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Salary cap dépassé : ${new_cap/1_000_000:.1f}M > $60M. Budget restant : ${(SALARY_CAP_MAX - current_cap)/1_000_000:.1f}M"
        )
    
    # 8. Mode Solo League : Pas de cooldown ni de limite de transferts
    # Les validations restantes : budget et positions
    
    # 9. Mode Solo League : Pas de limite de transferts
    
    # 10. Vérifier si la ligue est PRIVATE et si le joueur est déjà pris
    # Note : En MVP, on utilise seulement SOLO League, donc ce check est inactif
    league = db.query(League).filter(League.id == team.league_id).first()
    if league and league.type == LeagueType.PRIVATE:
        # Dans les ligues privées, un joueur ne peut être que dans une seule équipe
        player_taken = db.query(FantasyTeamPlayer).join(FantasyTeam).filter(
            and_(
                FantasyTeamPlayer.player_id == data.player_id,
                FantasyTeam.league_id == league.id
            )
        ).first()
        
        if player_taken:
            other_team = player_taken.team
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{player.full_name} est déjà dans l'équipe '{other_team.name}' de cette ligue privée"
            )
    
    # 11. Tout est OK ! Ajouter le joueur au roster
    new_roster_player = FantasyTeamPlayer(
        fantasy_team_id=team_id,
        player_id=data.player_id,
        roster_slot=data.position_slot,
        salary_at_acquisition=player.fantasy_cost,  # Geler le salaire actuel
        date_acquired=datetime.now()
    )
    db.add(new_roster_player)
    
    # 12. Mettre à jour le salary cap de l'équipe
    team.salary_cap_used = new_cap
    
    # 13. Vérifier si le roster est maintenant complet (6/6 joueurs)
    roster_count = db.query(FantasyTeamPlayer).filter(
        FantasyTeamPlayer.fantasy_team_id == team_id
    ).count() + 1  # +1 pour le joueur qu'on vient d'ajouter
    
    if roster_count >= 6 and not team.is_roster_complete:
        team.is_roster_complete = 1  # Marquer le roster comme complet
        # À partir de maintenant, la limite de 2 transferts/semaine s'applique
    
    # 14. Créer un Transfer pour l'historique (SEULEMENT si roster déjà complet)
    if team.is_roster_complete:
        transfer = Transfer(
            fantasy_team_id=team_id,
            player_id=data.player_id,
            transfer_type=TransferType.ADD,
            status=TransferStatus.COMPLETED,
            salary_at_transfer=player.fantasy_cost,
            processed_at=datetime.now()
        )
        db.add(transfer)
    
    # 15. Commit
    db.commit()
    db.refresh(team)
    
    # 16. Préparer le message de retour
    message = f"{player.full_name} a été ajouté à votre roster en position {data.position_slot.value}"
    
    # Message spécial si le roster vient d'être complété
    if roster_count == 6:
        message += f"\n🎉 Félicitations ! Votre roster est maintenant complet (6/6 joueurs). Votre équipe est active dans la Solo League."
    
    # Mode Solo League : Transferts illimités
    transfers_remaining = 999
    
    # 17. Retourner la réponse
    return AddPlayerResponse(
        message=message,
        player_added=PlayerRead.model_validate(player),
        position_slot=data.position_slot,
        salary_cap_used=new_cap,
        salary_cap_remaining=SALARY_CAP_MAX - new_cap,
        transfers_remaining_this_week=transfers_remaining
    )


# ========================================
# ENDPOINT 3 : DELETE /teams/{team_id}/roster/{player_id}
# ========================================

@router.delete("/{team_id}/roster/{player_id}", status_code=status.HTTP_200_OK)
def remove_player_from_roster(
    team_id: int,
    player_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ➖ Retire un joueur du roster
    
    Conséquences :
    - Le joueur est retiré de la position
    - Le salary cap est libéré (acquired_salary)
    - Un cooldown de 7 jours est appliqué (impossible de re-recruter ce joueur)
    - Un Transfer de type DROP est créé
    - Le compteur de transferts de la semaine est incrémenté
    
    Validations :
    - L'équipe existe et appartient à l'utilisateur
    - Le joueur est bien dans le roster
    - Moins de 2 transferts cette semaine
    """
    
    # 1. Vérifier que l'équipe existe
    team = db.query(FantasyTeam).filter(FantasyTeam.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipe introuvable"
        )
    
    # 2. Vérifier la propriété
    if team.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas propriétaire de cette équipe"
        )
    
    # 3. Vérifier que le joueur est dans le roster
    roster_player = db.query(FantasyTeamPlayer).filter(
        and_(
            FantasyTeamPlayer.fantasy_team_id == team_id,
            FantasyTeamPlayer.player_id == player_id
        )
    ).first()
    
    if not roster_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ce joueur n'est pas dans votre roster"
        )
    
    # 4. Mode Solo League : Pas de limite de transferts hebdomadaire
    
    # 5. Récupérer le joueur pour le message
    player = db.query(Player).filter(Player.id == player_id).first()
    
    # 6. Libérer le salary cap
    team.salary_cap_used = (team.salary_cap_used or 0.0) - roster_player.salary_at_acquisition
    
    # 7. Supprimer le joueur du roster
    db.delete(roster_player)
    
    # 8. Créer un Transfer de type DROP (pour le cooldown)
    transfer = Transfer(
        fantasy_team_id=team_id,
        player_id=player_id,
        transfer_type=TransferType.DROP,
        status=TransferStatus.COMPLETED,
        salary_at_transfer=roster_player.salary_at_acquisition,
        processed_at=datetime.now()
    )
    db.add(transfer)
    
    # 9. Commit
    db.commit()
    
    # 10. Retourner la confirmation
    return {
        "message": f"{player.full_name} a été retiré de votre roster",
        "player_removed": PlayerRead.model_validate(player),
        "position_freed": roster_player.roster_slot.value,
        "salary_cap_freed": roster_player.salary_at_acquisition,
        "salary_cap_remaining": SALARY_CAP_MAX - team.salary_cap_used
    }


# ========================================
# ENDPOINT 4 : GET /teams/{team_id}/available-players
# ========================================

@router.get("/{team_id}/available-players", response_model=AvailablePlayersResponse)
def get_available_players(
    team_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
    position: Optional[str] = Query(None, description="Filtrer par position (PG, SG, SF, PF, C)"),
    team_nba: Optional[str] = Query(None, description="Filtrer par équipe NBA (ex: LAL, GSW)"),
    max_salary: Optional[float] = Query(None, description="Salaire maximum en dollars"),
    search: Optional[str] = Query(None, description="Rechercher par nom"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    📋 Liste tous les joueurs disponibles pour une équipe
    
    Affiche les joueurs que l'équipe peut recruter selon :
    - Le budget restant (salary_cap_remaining)
    - Les positions libres dans le roster
    - Les cooldowns actifs (joueurs virés récemment)
    - Dans les Private Leagues : seulement les joueurs non pris
    
    Filtres disponibles :
    - position : PG, SG, SF, PF, C
    - team_nba : Code équipe NBA (LAL, GSW, etc.)
    - max_salary : Budget max
    - search : Recherche par nom
    
    Chaque joueur indique :
    - is_affordable : True si achetable avec le budget restant
    - has_cooldown : True si viré dans les 7 derniers jours
    - cooldown_ends : Date de fin du cooldown
    """
    
    # 1. Vérifier que l'équipe existe
    team = db.query(FantasyTeam).filter(FantasyTeam.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipe introuvable"
        )
    
    # 2. Vérifier la propriété
    if team.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas propriétaire de cette équipe"
        )
    
    # 3. Calculer le budget restant
    salary_cap_used = team.salary_cap_used or 0.0
    salary_cap_remaining = SALARY_CAP_MAX - salary_cap_used
    
    # 4. Trouver les positions libres
    roster_count = db.query(FantasyTeamPlayer).filter(
        FantasyTeamPlayer.fantasy_team_id == team_id
    ).count()
    
    available_positions = []
    all_positions = ['PG', 'SG', 'SF', 'PF', 'C', 'UTIL']
    
    for pos in all_positions:
        exists = db.query(FantasyTeamPlayer).filter(
            and_(
                FantasyTeamPlayer.fantasy_team_id == team_id,
                FantasyTeamPlayer.roster_slot == RosterSlot(pos)
            )
        ).first()
        if not exists:
            available_positions.append(pos)
    
    # 5. Récupérer les IDs des joueurs déjà dans le roster
    roster_player_ids = [
        rp.player_id for rp in db.query(FantasyTeamPlayer.player_id).filter(
            FantasyTeamPlayer.fantasy_team_id == team_id
        ).all()
    ]
    
    # 6. Dans les Private Leagues, exclure les joueurs déjà pris
    league = db.query(League).filter(League.id == team.league_id).first()
    excluded_player_ids = roster_player_ids.copy()
    
    if league and league.type == LeagueType.PRIVATE:
        # Récupérer tous les joueurs pris dans cette ligue
        taken_players = db.query(FantasyTeamPlayer.player_id).join(FantasyTeam).filter(
            FantasyTeam.league_id == league.id
        ).all()
        excluded_player_ids.extend([tp.player_id for tp in taken_players])
    
    # 7. Construire la requête de base (joueurs actifs non pris)
    query = db.query(Player).filter(
        and_(
            Player.is_active == True,
            ~Player.id.in_(excluded_player_ids)
        )
    )
    
    # 8. Appliquer les filtres
    if position:
        query = query.filter(Player.position == position.upper())
    
    if team_nba:
        query = query.filter(Player.team == team_nba.upper())
    
    if max_salary:
        query = query.filter(Player.fantasy_cost <= max_salary)
    else:
        # Par défaut, ne montrer que les joueurs abordables
        query = query.filter(Player.fantasy_cost <= salary_cap_remaining)
    
    if search:
        query = query.filter(
            or_(
                Player.first_name.ilike(f"%{search}%"),
                Player.last_name.ilike(f"%{search}%"),
                Player.full_name.ilike(f"%{search}%")
            )
        )
    
    # 9. Compter le total
    total_count = query.count()
    
    # 10. Appliquer la pagination
    players = query.order_by(Player.fantasy_cost.desc()).offset(skip).limit(limit).all()
    
    # 11. Construire la liste des joueurs disponibles (Mode Solo League - pas de cooldown)
    available_players = []
    for player in players:
        is_affordable = player.fantasy_cost <= salary_cap_remaining
        
        available_players.append(AvailablePlayerRead(
            player=PlayerRead.model_validate(player),
            is_affordable=is_affordable,
            has_cooldown=False,  # Pas de cooldown en Solo League
            cooldown_ends=None
        ))
    
    # 12. Retourner la réponse
    return AvailablePlayersResponse(
        team_id=team_id,
        salary_cap_remaining=salary_cap_remaining,
        available_positions=available_positions,
        players=available_players,
        total_count=total_count
    )

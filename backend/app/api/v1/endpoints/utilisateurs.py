"""
Endpoints pour les utilisateurs
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.utilisateur import Utilisateur
from app.schemas.auth import UtilisateurResponse

router = APIRouter()


@router.get("/moi")
async def obtenir_profil():
    """Obtenir le profil de l'utilisateur connecté"""
    return {"message": "Endpoint profil - À implémenter"}


@router.get("/{utilisateur_id}")
async def obtenir_utilisateur(utilisateur_id: int):
    """Obtenir les informations d'un utilisateur"""
    return {"message": f"Endpoint utilisateur {utilisateur_id} - À implémenter"}


# ============================================================================
# ENDPOINTS ADMINISTRATION
# ============================================================================

@router.get("/admin/all", response_model=List[UtilisateurResponse])
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Liste tous les utilisateurs de la plateforme
    
    **Permissions:** Administrateur uniquement
    """
    # Vérifier que l'utilisateur est admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    
    # Récupérer tous les utilisateurs
    users = db.query(Utilisateur).order_by(Utilisateur.date_creation.desc()).all()
    
    return users


@router.patch("/admin/{user_id}/promote", response_model=UtilisateurResponse)
async def promote_user_to_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Promouvoir un utilisateur en administrateur
    
    **Permissions:** Administrateur uniquement
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur {user_id} introuvable"
        )
    
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{user.nom_utilisateur} est déjà administrateur"
        )
    
    user.is_admin = True
    db.commit()
    db.refresh(user)
    
    return user


@router.patch("/admin/{user_id}/demote", response_model=UtilisateurResponse)
async def demote_admin_to_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Rétrograder un administrateur en utilisateur normal
    
    **Permissions:** Administrateur uniquement
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur {user_id} introuvable"
        )
    
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{user.nom_utilisateur} n'est pas administrateur"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas vous rétrograder vous-même"
        )
    
    user.is_admin = False
    db.commit()
    db.refresh(user)
    
    return user

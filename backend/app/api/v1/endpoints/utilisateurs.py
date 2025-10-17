"""
Endpoints pour les utilisateurs
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/moi")
async def obtenir_profil():
    """Obtenir le profil de l'utilisateur connecté"""
    return {"message": "Endpoint profil - À implémenter"}


@router.get("/{utilisateur_id}")
async def obtenir_utilisateur(utilisateur_id: int):
    """Obtenir les informations d'un utilisateur"""
    return {"message": f"Endpoint utilisateur {utilisateur_id} - À implémenter"}

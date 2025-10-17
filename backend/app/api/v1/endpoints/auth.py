"""
Endpoints pour l'authentification
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/inscription")
async def inscription():
    """Créer un nouveau compte utilisateur"""
    return {"message": "Endpoint d'inscription - À implémenter"}


@router.post("/connexion")
async def connexion():
    """Se connecter et obtenir un token JWT"""
    return {"message": "Endpoint de connexion - À implémenter"}

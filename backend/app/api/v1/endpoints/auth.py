"""
Endpoints pour l'authentification

Ce fichier contient:
- POST /inscription - Créer un nouveau compte utilisateur
- POST /connexion - Se connecter et obtenir un token JWT
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import hash_password, verify_password, create_access_token
from app.models.utilisateur import Utilisateur
from app.schemas.auth import (
    UtilisateurInscription,
    UtilisateurConnexion,
    UtilisateurResponse,
    Token
)

router = APIRouter()


# ========================================
# ENDPOINT 1: INSCRIPTION
# ========================================

@router.post(
    "/inscription",
    response_model=UtilisateurResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouveau compte utilisateur",
    description="Inscrit un nouvel utilisateur avec un nom d'utilisateur et un mot de passe"
)
def inscription(
    user_data: UtilisateurInscription,
    db: Session = Depends(get_db)
):
    """
    Créer un nouveau compte utilisateur
    
    Args:
        user_data: Les données d'inscription (nom_utilisateur, mot_de_passe)
        db: Session de base de données (injectée automatiquement)
    
    Returns:
        Les informations de l'utilisateur créé
    
    Raises:
        HTTPException 400: Si le nom d'utilisateur existe déjà
    
    Exemple de requête:
        POST /api/v1/auth/inscription
        {
            "nom_utilisateur": "alice",
            "mot_de_passe": "alice123"
        }
    
    Exemple de réponse:
        {
            "id": 1,
            "nom_utilisateur": "alice",
            "date_creation": "2025-10-18T10:30:00Z"
        }
    """
    
    # 1. Vérifier si l'utilisateur existe déjà
    existing_user = db.query(Utilisateur).filter(
        Utilisateur.nom_utilisateur == user_data.nom_utilisateur
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà pris"
        )
    
    # 2. Hasher le mot de passe
    hashed_password = hash_password(user_data.mot_de_passe)
    
    # 3. Créer le nouvel utilisateur
    new_user = Utilisateur(
        nom_utilisateur=user_data.nom_utilisateur,
        mot_de_passe_hash=hashed_password
    )
    
    # 4. Sauvegarder en base de données
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Récupérer l'ID et date_creation générés
    
    # 5. Retourner l'utilisateur créé (sans le mot de passe!)
    return new_user


# ========================================
# ENDPOINT 2: CONNEXION
# ========================================

@router.post(
    "/connexion",
    response_model=Token,
    summary="Se connecter et obtenir un token JWT",
    description="Authentifie un utilisateur et retourne un token JWT"
)
def connexion(
    credentials: UtilisateurConnexion,
    db: Session = Depends(get_db)
):
    """
    Se connecter et obtenir un token JWT
    
    Args:
        credentials: Les identifiants (nom_utilisateur, mot_de_passe)
        db: Session de base de données (injectée automatiquement)
    
    Returns:
        Un token JWT pour s'authentifier sur les endpoints protégés
    
    Raises:
        HTTPException 401: Si les identifiants sont incorrects
    
    Exemple de requête:
        POST /api/v1/auth/connexion
        {
            "nom_utilisateur": "alice",
            "mot_de_passe": "alice123"
        }
    
    Exemple de réponse:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    
    Utilisation du token:
        Pour les requêtes suivantes, ajouter dans les headers:
        Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    
    # 1. Chercher l'utilisateur dans la base de données
    user = db.query(Utilisateur).filter(
        Utilisateur.nom_utilisateur == credentials.nom_utilisateur
    ).first()
    
    # 2. Vérifier que l'utilisateur existe
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 3. Vérifier le mot de passe
    if not verify_password(credentials.mot_de_passe, user.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 4. Créer le token JWT
    access_token = create_access_token(
        data={"sub": user.nom_utilisateur}
    )
    
    # 5. Retourner le token
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

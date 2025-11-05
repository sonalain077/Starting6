"""
Gestion de l'authentification JWT avec HS256

Ce fichier gère:
- Hashage des mots de passe avec bcrypt
- Création de tokens JWT
- Vérification de tokens JWT
- Dépendance get_current_user pour protéger les endpoints
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt  # ← Utiliser bcrypt directement
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.utilisateur import Utilisateur

# Schéma OAuth2 pour extraire le token depuis le header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


# ========================================
# PARTIE 1: HASHAGE DES MOTS DE PASSE
# ========================================

def hash_password(password: str) -> str:
    """
    Hash un mot de passe en clair avec bcrypt
    
    Args:
        password: Le mot de passe en clair
        
    Returns:
        Le hash bcrypt du mot de passe
    """
    # Convertir le mot de passe en bytes
    password_bytes = password.encode('utf-8')
    
    # Générer un salt et hasher
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Retourner le hash sous forme de string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie qu'un mot de passe en clair correspond au hash
    
    Args:
        plain_password: Le mot de passe en clair à vérifier
        hashed_password: Le hash bcrypt stocké en BDD
        
    Returns:
        True si le mot de passe est correct, False sinon
    """
    # Convertir en bytes
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    
    # Vérifier le mot de passe
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ========================================
# PARTIE 2: TOKENS JWT
# ========================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT signé avec HS256
    
    Args:
        data: Les données à encoder dans le token (généralement {"sub": username})
        expires_delta: Durée de validité personnalisée (optionnel)
        
    Returns:
        Le token JWT sous forme de string
    """
    to_encode = data.copy()
    
    # Définir la date d'expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Créer le token JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """
    Décode et valide un token JWT
    
    Args:
        token: Le token JWT à décoder
        
    Returns:
        Le nom d'utilisateur (sub) si le token est valide, None sinon
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        
        if username is None:
            return None
            
        return username
        
    except JWTError:
        return None


# ========================================
# PARTIE 3: DÉPENDANCE FASTAPI
# ========================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Utilisateur:
    """
    Dépendance FastAPI pour extraire l'utilisateur courant depuis le token JWT
    
    Usage dans un endpoint:
        @router.get("/me")
        def get_my_profile(current_user: Utilisateur = Depends(get_current_user)):
            return current_user
    
    Args:
        token: Le token JWT extrait du header Authorization
        db: Session de base de données
        
    Returns:
        L'utilisateur authentifié
        
    Raises:
        HTTPException 401: Si le token est invalide ou l'utilisateur n'existe pas
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Décoder le token
    username = decode_access_token(token)
    if username is None:
        raise credentials_exception
    
    # Chercher l'utilisateur en BDD
    user = db.query(Utilisateur).filter(Utilisateur.nom_utilisateur == username).first()
    if user is None:
        raise credentials_exception
    
    return user
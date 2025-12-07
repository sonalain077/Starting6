"""
Schémas Pydantic pour l'authentification

Les schémas définissent:
- La structure des données d'entrée (Request)
- La structure des données de sortie (Response)
- La validation automatique
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime


# ========================================
# SCHÉMAS DE REQUÊTE (Input)
# ========================================

class UtilisateurInscription(BaseModel):
    """
    Schéma pour l'inscription d'un nouvel utilisateur
    
    Utilisé par: POST /api/v1/auth/inscription
    
    Exemple:
        {
            "nom_utilisateur": "alice",
            "mot_de_passe": "alice123"
        }
    """
    nom_utilisateur: str = Field(
        ...,  # ... = obligatoire
        min_length=3,
        max_length=50,
        description="Nom d'utilisateur (3-50 caractères)"
    )
    
    mot_de_passe: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Mot de passe (minimum 6 caractères)"
    )
    
    @validator('nom_utilisateur')
    def nom_utilisateur_valide(cls, v):
        """
        Valide que le nom d'utilisateur ne contient pas d'espaces
        """
        if ' ' in v:
            raise ValueError("Le nom d'utilisateur ne peut pas contenir d'espaces")
        return v.lower()  # Convertir en minuscules


class UtilisateurConnexion(BaseModel):
    """
    Schéma pour la connexion d'un utilisateur
    
    Utilisé par: POST /api/v1/auth/connexion
    
    Exemple:
        {
            "nom_utilisateur": "alice",
            "mot_de_passe": "alice123"
        }
    """
    nom_utilisateur: str = Field(
        ...,
        description="Nom d'utilisateur"
    )
    
    mot_de_passe: str = Field(
        ...,
        description="Mot de passe"
    )


# ========================================
# SCHÉMAS DE RÉPONSE (Output)
# ========================================

class Token(BaseModel):
    """
    Schéma pour la réponse contenant le token JWT
    
    Retourné par: POST /api/v1/auth/connexion
    
    Exemple:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    access_token: str = Field(
        ...,
        description="Token JWT pour l'authentification"
    )
    
    token_type: str = Field(
        default="bearer",
        description="Type de token (toujours 'bearer' pour JWT)"
    )


class UtilisateurResponse(BaseModel):
    """
    Schéma pour la réponse contenant les infos d'un utilisateur
    
    Retourné par: POST /api/v1/auth/inscription
    
    Exemple:
        {
            "id": 1,
            "nom_utilisateur": "alice",
            "date_creation": "2025-10-18T10:30:00Z"
        }
    """
    id: int = Field(
        ...,
        description="Identifiant unique de l'utilisateur"
    )
    
    nom_utilisateur: str = Field(
        ...,
        description="Nom d'utilisateur"
    )
    
    date_creation: datetime = Field(
        ...,
        description="Date de création du compte"
    )
    
    is_admin: bool = Field(
        default=False,
        description="Indique si l'utilisateur est administrateur"
    )
    
    class Config:
        # Permet de convertir automatiquement depuis un modèle SQLAlchemy
        from_attributes = True

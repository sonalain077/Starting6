'use client';

/**
 * AUTH CONTEXT - Le cerveau de l'authentification
 * 
 * Ce Context React gère l'état global de l'utilisateur connecté.
 * Il est accessible depuis n'importe quel composant de l'app.
 * 
 * Fonctionnalités :
 * - Stocke l'utilisateur connecté (user)
 * - Fournit l'état d'authentification (isAuthenticated)
 * - Gère le loading initial (vérifie le token au démarrage)
 * - Fonctions login/logout centralisées
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '@/lib/types';
import * as api from '@/lib/api';

// ============================================================================
// TYPES
// ============================================================================

interface AuthContextType {
  user: User | null;                          // Utilisateur connecté (null si pas connecté)
  isAuthenticated: boolean;                   // true si user connecté
  isLoading: boolean;                         // true pendant la vérification du token
  login: (nom_utilisateur: string, mot_de_passe: string) => Promise<void>;  // Fonction de connexion
  register: (nom_utilisateur: string, mot_de_passe: string) => Promise<void>;  // Fonction d'inscription
  logout: () => void;                         // Fonction de déconnexion
}

// ============================================================================
// CRÉATION DU CONTEXT
// ============================================================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ============================================================================
// PROVIDER COMPONENT
// ============================================================================

/**
 * AuthProvider - Enveloppe toute l'application
 * 
 * Ce composant doit entourer ton app dans layout.tsx :
 * <AuthProvider>
 *   <App />
 * </AuthProvider>
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // ============================================================================
  // VÉRIFICATION DU TOKEN AU DÉMARRAGE
  // ============================================================================

  /**
   * Au chargement de l'app, vérifie si un token existe dans localStorage.
   * Si oui, récupère les infos de l'utilisateur depuis le backend.
   * 
   * C'est ce qui permet de rester connecté après un refresh de page !
   */
  useEffect(() => {
    const checkAuth = async () => {
      const token = api.getToken();
      
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        // Pour l'instant, on crée un user temporaire depuis le token
        // Plus tard, quand l'endpoint /utilisateurs/moi sera implémenté :
        // const currentUser = await api.getCurrentUser();
        
        // Temporaire : on crée un user minimal
        setUser({
          id: 0,
          nom_utilisateur: 'user',
          date_creation: new Date().toISOString(),
        });
      } catch (error) {
        console.error('Token invalide ou expiré:', error);
        // Si le token est invalide, on le supprime
        api.removeToken();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []); // [] = s'exécute une seule fois au montage du composant

  // ============================================================================
  // FONCTION LOGIN
  // ============================================================================

  /**
   * Connecte un utilisateur
   * 
   * Flux :
   * 1. Appelle api.login() (qui envoie nom_utilisateur + mot_de_passe au backend)
   * 2. Le backend renvoie un JWT token
   * 3. On stocke le token dans localStorage (via api.setToken)
   * 4. On récupère les infos user depuis le token ou le backend
   */
  const login = async (nom_utilisateur: string, mot_de_passe: string) => {
    try {
      const response = await api.login({ nom_utilisateur, mot_de_passe });
      
      // Stocke le token dans localStorage
      api.setToken(response.access_token);
      
      // Pour l'instant, on crée un objet user temporaire
      // Plus tard, on pourra appeler getCurrentUser() si l'endpoint est implémenté
      setUser({
        id: 0, // Temporaire
        nom_utilisateur: nom_utilisateur,
        date_creation: new Date().toISOString(),
      });
    } catch (error) {
      // Remonte l'erreur au composant qui appelle login()
      throw error;
    }
  };

  // ============================================================================
  // FONCTION REGISTER
  // ============================================================================

  /**
   * Inscrit un nouvel utilisateur
   * 
   * Même flux que login :
   * 1. Appelle api.register()
   * 2. Le backend crée l'utilisateur et renvoie un token
   * 3. On stocke le token et l'user
   */
  const register = async (nom_utilisateur: string, mot_de_passe: string) => {
    try {
      const response = await api.register({ nom_utilisateur, mot_de_passe });
      
      api.setToken(response.access_token);
      
      // Crée un objet user temporaire
      setUser({
        id: 0, // Temporaire
        nom_utilisateur: nom_utilisateur,
        date_creation: new Date().toISOString(),
      });
    } catch (error) {
      throw error;
    }
  };

  // ============================================================================
  // FONCTION LOGOUT
  // ============================================================================

  /**
   * Déconnecte l'utilisateur
   * 
   * Flux :
   * 1. Supprime le token du localStorage
   * 2. Réinitialise l'état user à null
   * 3. (Optionnel) Appelle le backend pour invalider le token
   */
  const logout = () => {
    api.removeToken();
    setUser(null);
    
    // Optionnel : appeler api.logout() si tu veux une invalidation côté serveur
    // Pour l'instant, on fait juste du côté client (suffit pour JWT)
  };

  // ============================================================================
  // VALEUR DU CONTEXT
  // ============================================================================

  /**
   * Tout ce qui est dans cette valeur sera accessible
   * depuis n'importe quel composant qui utilise useAuth()
   */
  const value: AuthContextType = {
    user,
    isAuthenticated: !!user, // !! convertit en boolean (null -> false, objet -> true)
    isLoading,
    login,
    register,
    logout,
  };

  // Affiche un loader pendant la vérification du token
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          <p className="mt-2 text-sm text-muted-foreground">Vérification...</p>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// ============================================================================
// HOOK PERSONNALISÉ
// ============================================================================

/**
 * useAuth() - Hook pour accéder au Context depuis n'importe quel composant
 * 
 * Utilisation :
 * 
 * function MonComposant() {
 *   const { user, isAuthenticated, login, logout } = useAuth();
 *   
 *   if (!isAuthenticated) {
 *     return <div>Pas connecté</div>
 *   }
 *   
 *   return <div>Bonjour {user.username}</div>
 * }
 */
export function useAuth() {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider');
  }
  
  return context;
}

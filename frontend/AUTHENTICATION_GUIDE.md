# 🎉 SYSTÈME D'AUTHENTIFICATION TERMINÉ !

## ✅ Ce qui a été créé

### 1. **Auth Context** (`src/context/auth-context.tsx`)
Le **cerveau de l'authentification** qui gère l'état global de l'utilisateur.

**Fonctionnalités :**
- Stocke l'utilisateur connecté dans l'état React
- Vérifie automatiquement le token au démarrage de l'app
- Fournit des fonctions `login()`, `register()`, `logout()`
- Expose `isAuthenticated` et `isLoading`

**Comment ça marche ?**
```typescript
// Dans n'importe quel composant :
const { user, isAuthenticated, login, logout } = useAuth();

// Pour se connecter :
await login(username, password);

// Pour savoir si connecté :
if (isAuthenticated) {
  console.log("Connecté en tant que", user.username);
}
```

---

### 2. **API Client** (`src/lib/api.ts`)
Le **pont entre le frontend et le backend**.

**Fonctionnalités :**
- Fonctions pour toutes les requêtes API (login, register, getPlayers, etc.)
- Gestion automatique du token JWT dans les headers
- Stockage du token dans `localStorage`
- Gestion des erreurs

**Comment ça marche ?**
```typescript
// Le frontend appelle l'API :
const players = await api.getPlayers();

// En coulisses :
// 1. Récupère le token du localStorage
// 2. Envoie une requête HTTP à http://localhost:8000/api/v1/players
// 3. Ajoute le header Authorization: Bearer <token>
// 4. Renvoie les données en JSON
```

---

### 3. **Pages créées**

#### **Page d'accueil** (`/`) - `src/app/page.tsx`
- Landing page avec présentation du projet
- Boutons "Créer mon équipe" et "Se connecter"
- Redirige automatiquement vers `/dashboard` si déjà connecté

#### **Page Login** (`/login`) - `src/app/login/page.tsx`
- Formulaire de connexion (username + password)
- Validation des champs
- Affichage des erreurs
- Redirection vers `/dashboard` après succès
- Lien vers la page Register

#### **Page Register** (`/register`) - `src/app/register/page.tsx`
- Formulaire d'inscription (username, email, password, confirmation)
- Validations :
  * Username : min 3 caractères
  * Email : format valide
  * Password : min 8 caractères
  * Passwords doivent correspondre
- Redirection vers `/dashboard` après succès
- Lien vers la page Login

#### **Page Dashboard** (`/dashboard`) - `src/app/dashboard/page.tsx`
- Page protégée (redirige vers `/login` si pas connecté)
- Affiche les infos de l'utilisateur connecté
- Bouton de déconnexion
- Cards temporaires pour les futures fonctionnalités

---

### 4. **Layout racine** (`src/app/layout.tsx`)
- Enveloppe toute l'app avec le `<AuthProvider>`
- Permet à tous les composants d'accéder au contexte d'authentification

---

## 🔄 Flux d'Authentification

### **Inscription d'un nouvel utilisateur**
```
1. User remplit le formulaire (/register)
2. Clique sur "Créer mon compte"
3. Frontend → api.register() → Backend POST /api/v1/auth/register
4. Backend crée l'utilisateur dans PostgreSQL
5. Backend renvoie { access_token, user }
6. Frontend stocke le token dans localStorage
7. Frontend met à jour le AuthContext avec l'user
8. Redirection vers /dashboard
```

### **Connexion d'un utilisateur existant**
```
1. User remplit le formulaire (/login)
2. Clique sur "Se connecter"
3. Frontend → api.login() → Backend POST /api/v1/auth/token
4. Backend vérifie username + password dans PostgreSQL
5. Backend renvoie { access_token, user }
6. Frontend stocke le token dans localStorage
7. Frontend met à jour le AuthContext avec l'user
8. Redirection vers /dashboard
```

### **Persistance de la session**
```
1. User refresh la page ou revient plus tard
2. AuthContext se monte et exécute useEffect()
3. Vérifie si un token existe dans localStorage
4. Si oui → api.getCurrentUser() → Backend GET /api/v1/users/me
5. Backend vérifie le token JWT
6. Si valide → renvoie les infos user
7. Si invalide → supprime le token et déconnecte
8. User reste connecté sans re-login !
```

### **Déconnexion**
```
1. User clique sur "Se déconnecter"
2. Frontend → logout()
3. Supprime le token du localStorage
4. Réinitialise l'user à null dans le AuthContext
5. Redirection vers /login
```

---

## 🧩 Architecture Frontend ↔ Backend

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js)                     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              AuthContext (State Global)              │  │
│  │  - user: User | null                                 │  │
│  │  - isAuthenticated: boolean                          │  │
│  │  - login(), register(), logout()                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                             ↕                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Pages (Composants React)                │  │
│  │  - / (Home)                                          │  │
│  │  - /login (Login)                                    │  │
│  │  - /register (Register)                              │  │
│  │  - /dashboard (Dashboard)                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                             ↕                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Client (src/lib/api.ts)             │  │
│  │  - login(credentials) → POST /auth/token             │  │
│  │  - register(data) → POST /auth/register              │  │
│  │  - getCurrentUser() → GET /users/me                  │  │
│  │  - getPlayers() → GET /players                       │  │
│  │  - ...                                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                             ↕                               │
└─────────────────────────────────────────────────────────────┘
                              │
                    HTTP Requests (JSON)
                    + Header: Authorization: Bearer <token>
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                      │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  API Endpoints                       │  │
│  │  POST /api/v1/auth/register                          │  │
│  │  POST /api/v1/auth/token                             │  │
│  │  GET  /api/v1/users/me (protected)                   │  │
│  │  GET  /api/v1/players (protected)                    │  │
│  │  ...                                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                             ↕                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Auth Middleware                         │  │
│  │  - Vérifie le token JWT                             │  │
│  │  - Extrait le user_id                               │  │
│  │  - Inject current_user dans la requête              │  │
│  └──────────────────────────────────────────────────────┘  │
│                             ↕                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Services + Models (SQLAlchemy)          │  │
│  │  - Queries PostgreSQL                                │  │
│  │  - Business logic                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                             ↕                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     DATABASE (PostgreSQL)                   │
│  - Table utilisateurs                                       │
│  - Table players                                            │
│  - Table fantasy_teams                                      │
│  - ...                                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 Comment Tester

### 1. **Vérifier que le backend est lancé**
```bash
# Dans un terminal
cd backend
python -m app.main
# Doit tourner sur http://localhost:8000
```

### 2. **Vérifier que le frontend est lancé**
```bash
# Dans un autre terminal
cd frontend
npm run dev
# Doit tourner sur http://localhost:3000
```

### 3. **Tester l'inscription**
1. Ouvre http://localhost:3000
2. Clique sur "Créer mon équipe"
3. Remplis le formulaire :
   - Username : `testuser`
   - Email : `test@example.com`
   - Password : `password123`
   - Confirme le password
4. Clique sur "Créer mon compte"
5. Tu devrais être redirigé vers `/dashboard`
6. Tu devrais voir "Bienvenue, testuser !"

### 4. **Tester la persistance**
1. Refresh la page (F5)
2. Tu devrais rester connecté !
3. Vérifie dans DevTools → Application → Local Storage → `access_token`

### 5. **Tester la déconnexion**
1. Clique sur "Se déconnecter"
2. Tu es redirigé vers `/login`
3. Le token a été supprimé du localStorage

### 6. **Tester la connexion**
1. Va sur `/login`
2. Entre les identifiants créés précédemment
3. Clique sur "Se connecter"
4. Tu es redirigé vers `/dashboard`

---

## 🎯 Prochaines Étapes

### Semaine 1 (en cours) - Setup & Auth
- ✅ Next.js + shadcn/ui
- ✅ TypeScript types
- ✅ API client
- ✅ Auth Context
- ✅ Pages Login/Register/Dashboard
- ⏳ **TODO** : Middleware pour protéger les routes automatiquement

### Semaine 2 - Dashboard & Mon Équipe
- [ ] Afficher les infos de l'équipe (salary cap, score, rank)
- [ ] Page "Mon Équipe" avec les 6 joueurs du roster
- [ ] Système de création d'équipe si pas encore créée

### Semaine 3 - Transferts & Joueurs
- [ ] Page liste des joueurs NBA (avec filtres par poste)
- [ ] Modal de transfert (ajouter/remplacer un joueur)
- [ ] Validation du salary cap en temps réel

### Semaine 4 - Leaderboard & Polish
- [ ] Page classement global (Solo League)
- [ ] Graphiques d'évolution des scores
- [ ] Page de profil utilisateur

---

## 💡 Concepts Clés à Retenir

### 1. **React Context**
Un "state global" accessible depuis n'importe quel composant.  
Au lieu de passer des props de composant en composant, on utilise `useAuth()` partout.

### 2. **JWT Token**
Un jeton d'authentification stocké côté client.  
Contient l'ID de l'utilisateur + une signature cryptée.  
Le backend vérifie la signature pour savoir si le token est valide.

### 3. **localStorage**
Un stockage persistant dans le navigateur.  
Permet de garder le token même après un refresh de page.

### 4. **Client Components (`'use client'`)**
En Next.js 15, les composants sont "Server Components" par défaut.  
On doit ajouter `'use client'` pour utiliser les hooks React (useState, useEffect, useContext).

### 5. **Protected Routes**
Des pages accessibles uniquement aux utilisateurs connectés.  
On vérifie `isAuthenticated` dans un `useEffect` et on redirige vers `/login` si false.

---

## 🔧 Fichiers Modifiés / Créés

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx               ← Modifié (ajout AuthProvider)
│   │   ├── page.tsx                 ← Modifié (landing page)
│   │   ├── login/
│   │   │   └── page.tsx             ← Créé
│   │   ├── register/
│   │   │   └── page.tsx             ← Créé
│   │   └── dashboard/
│   │       └── page.tsx             ← Créé
│   ├── context/
│   │   └── auth-context.tsx         ← Créé
│   ├── lib/
│   │   ├── api.ts                   ← Créé
│   │   └── types.ts                 ← Créé
│   └── components/
│       └── ui/
│           ├── button.tsx           ← Créé (shadcn)
│           ├── input.tsx            ← Créé (shadcn)
│           ├── label.tsx            ← Créé (shadcn)
│           ├── card.tsx             ← Créé (shadcn)
│           └── form.tsx             ← Créé (shadcn)
```

---

## 🎓 Explications Pédagogiques

### Pourquoi séparer frontend et backend ?

**Frontend (Next.js)** :
- Responsable de l'interface utilisateur
- S'exécute dans le navigateur
- Ne peut PAS accéder directement à la base de données
- Fait des requêtes HTTP au backend

**Backend (FastAPI)** :
- Responsable de la logique métier
- S'exécute sur un serveur
- Seul à pouvoir accéder à la base de données
- Renvoie des données en JSON

**Avantages** :
- Sécurité : Le frontend ne voit jamais les secrets de la DB
- Scalabilité : On peut déployer frontend et backend séparément
- Flexibilité : On peut créer une app mobile qui utilise le même backend

### Comment le token JWT fonctionne ?

1. **User se connecte** → Backend génère un token JWT
2. **Token contient** : `{ user_id: 123, exp: 1234567890 }` (+ signature)
3. **Frontend stocke** le token dans localStorage
4. **À chaque requête**, le frontend envoie le token dans le header
5. **Backend vérifie** la signature → Si valide, extrait le user_id
6. **Backend retourne** les données de l'utilisateur 123

**Sécurité** :
- Le token est signé avec une clé secrète (côté backend)
- Impossible de modifier le token sans connaître la clé
- Le token a une date d'expiration

---

## 🚀 Ton système d'authentification est COMPLET !

Tu peux maintenant :
- ✅ Créer un compte
- ✅ Te connecter
- ✅ Rester connecté après un refresh
- ✅ Te déconnecter
- ✅ Protéger des pages (dashboard)

La suite : construire les vraies pages de l'app (Mon Équipe, Transferts, Leaderboard) ! 🎯

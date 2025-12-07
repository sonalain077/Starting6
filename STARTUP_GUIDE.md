# 🚀 Scripts de Démarrage Automatique

## Démarrage rapide

### Windows PowerShell

**Lancer tout le projet (DB + Backend + Frontend) :**
```powershell
.\start_project.ps1
```

**Arrêter tout le projet :**
```powershell
.\stop_project.ps1
```

---

## Ce que fait `start_project.ps1`

Le script lance automatiquement dans l'ordre :

1. **PostgreSQL** (Docker) sur le port **5432**
   - Vérifie si Docker est actif
   - Démarre ou crée le conteneur `nba_fantasy_db`
   - Attend que PostgreSQL soit prêt

2. **Backend FastAPI** sur **http://localhost:8000**
   - Lance Uvicorn avec hot-reload
   - Ouvre un nouveau terminal PowerShell pour le backend
   - Vérifie que l'API est accessible

3. **Frontend Next.js** sur **http://localhost:3000**
   - Installe les dépendances si nécessaire (première fois)
   - Lance le serveur de développement Next.js
   - Ouvre un nouveau terminal PowerShell pour le frontend

---

## Prérequis

- ✅ **Docker Desktop** installé et démarré
- ✅ **Python 3.11+** installé
- ✅ **Node.js 18+** installé
- ✅ Fichier `.env` configuré à la racine du projet

---

## Utilisation

### Première utilisation

```powershell
# Cloner le projet
git clone <repo-url>
cd ProjetFullstack

# Installer les dépendances Python (backend)
cd backend
pip install -r requirements.txt
cd ..

# Lancer le projet
.\start_project.ps1
```

### Utilisation quotidienne

```powershell
# Lancer tout
.\start_project.ps1

# Travailler...

# Arrêter tout
.\stop_project.ps1
```

---

## Accès après démarrage

Une fois le script exécuté, vous pouvez accéder à :

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Interface utilisateur |
| **Backend API** | http://localhost:8000 | API REST |
| **Swagger Docs** | http://localhost:8000/docs | Documentation interactive |
| **PostgreSQL** | localhost:5432 | Base de données |

### Pages frontend disponibles :

- **Accueil** : http://localhost:3000
- **Inscription** : http://localhost:3000/register
- **Connexion** : http://localhost:3000/login
- **Dashboard** : http://localhost:3000/dashboard
- **Mon Équipe** : http://localhost:3000/team
- **Joueurs NBA** : http://localhost:3000/players
- **Leaderboard** : http://localhost:3000/leaderboard

---

## Notes importantes

⚠️ **Ne fermez PAS les terminaux ouverts automatiquement** (Backend et Frontend) pendant que vous travaillez. Ils doivent rester actifs pour que les serveurs fonctionnent.

✅ **Pour arrêter proprement** : Utilisez `.\stop_project.ps1` qui tue tous les processus et arrête Docker.

🔄 **Hot-reload activé** : Les modifications du code sont automatiquement détectées et appliquées (backend et frontend).

---

## Dépannage

### Le script ne se lance pas

**Erreur : "Execution Policy"**
```powershell
# Autoriser l'exécution de scripts (une seule fois)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Docker n'est pas accessible

```powershell
# Vérifier que Docker Desktop est démarré
docker info
```

Si ça ne fonctionne pas, lancez Docker Desktop manuellement.

### Le backend ne démarre pas

Vérifier que Python et les dépendances sont installées :
```powershell
cd backend
python --version
pip install -r requirements.txt
```

### Le frontend ne démarre pas

Vérifier que Node.js est installé et installer les dépendances :
```powershell
cd frontend
node --version
npm install
```

### Port déjà utilisé

Si un port (3000 ou 8000) est déjà utilisé :

```powershell
# Trouver le processus sur le port 8000
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess

# Tuer le processus (remplacer PID)
Stop-Process -Id <PID> -Force
```

---

## Alternative : Lancement manuel

Si vous préférez lancer les services manuellement :

```powershell
# Terminal 1 : PostgreSQL
docker-compose up -d db

# Terminal 2 : Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3 : Frontend
cd frontend
npm run dev
```

---

## Workflow recommandé

```powershell
# Matin : Lancer le projet
.\start_project.ps1

# Développer toute la journée avec hot-reload actif...

# Soir : Arrêter le projet
.\stop_project.ps1
```

Profitez du développement ! 🏀🚀

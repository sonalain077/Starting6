# GitHub Actions CI/CD Pipeline - NBA Fantasy League

## 📋 Vue d'ensemble

Ce projet utilise GitHub Actions pour automatiser les tests et la validation du code à chaque push ou pull request.

## 🔄 Workflow CI/CD

### Déclenchement
- **Push** sur les branches `main` et `mvp1`
- **Pull Request** vers les branches `main` et `mvp1`

### Jobs exécutés

#### 1. **Test Backend** (`test-backend`)
- Configure PostgreSQL 15 en service
- Installe Python 3.11
- Installe les dépendances depuis `requirements.txt`
- Exécute les 18 tests avec pytest
- **Durée**: ~2-3 minutes

#### 2. **Lint Backend** (`lint-backend`)
- Vérifie la qualité du code Python avec flake8
- Détecte les erreurs syntaxiques
- Vérifie la complexité du code
- **Durée**: ~30 secondes

#### 3. **Build Frontend** (`test-frontend`)
- Configure Node.js 20
- Installe les dépendances npm
- Build l'application Next.js
- **Durée**: ~2-3 minutes

#### 4. **Docker Build** (`docker-build`)
- Valide la configuration docker-compose
- Build toutes les images Docker
- **Durée**: ~5-7 minutes

#### 5. **Summary** (`summary`)
- Résume les résultats de tous les jobs
- S'exécute toujours, même en cas d'échec

## 📊 Résultats attendus

✅ **18 tests backend** doivent passer  
✅ **Pas d'erreurs de lint**  
✅ **Build frontend** réussi  
✅ **Build Docker** réussi  

## 🚀 Optimisations

- **Cache pip**: Accélère l'installation des dépendances Python
- **Cache npm**: Accélère l'installation des dépendances Node.js
- **Tests en parallèle**: Les 4 jobs principaux s'exécutent simultanément

## 🔍 Vérification locale

Avant de pusher, tu peux vérifier localement:

```bash
# Tests backend
cd backend
pytest tests/ -v

# Lint backend
flake8 app/ --count --max-line-length=127

# Build frontend
cd frontend
npm run build

# Docker
docker-compose build
```

## 📈 Badges (optionnel)

Ajoute ce badge dans ton README.md:

```markdown
![CI/CD](https://github.com/sonalain077/Starting6/workflows/CI%2FCD%20Pipeline/badge.svg?branch=mvp1)
```

## 🛠️ Configuration

Les variables d'environnement pour les tests sont définies dans le workflow:
- `DATABASE_URL`: Base de test PostgreSQL
- `SECRET_KEY`: Clé de test pour JWT
- `NEXT_PUBLIC_API_URL`: URL de l'API pour le frontend

## 📝 Logs

Les logs de chaque job sont disponibles dans l'onglet **Actions** de GitHub après chaque exécution.

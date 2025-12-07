FROM node:20-alpine

WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier le code source
COPY . .

# Exposer le port Next.js
EXPOSE 3000

# Commande de démarrage (mode développement)
CMD ["npm", "run", "dev"]

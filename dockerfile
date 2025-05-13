# Utiliser l'image officielle Python
FROM python:3.10

# Définir le répertoire de travail
WORKDIR /

# Copier le fichier requirements.txt
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du projet
COPY . .

# Exposer le port Flask
EXPOSE 5000

# Commande pour démarrer l'application Flask
CMD ["python", "app.py"]

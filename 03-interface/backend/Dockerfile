# On part d'une image Python légère
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Installation des dépendances système (pour pg_isready)
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .
COPY start.sh .

# Rendre le script exécutable
RUN chmod +x start.sh

# Lancement via le script de démarrage
CMD ["./start.sh"]
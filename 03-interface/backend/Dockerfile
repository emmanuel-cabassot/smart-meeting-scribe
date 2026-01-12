# On part d'une image Python légère
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /code

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY app ./app

# Lancement de l'API sur le port 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
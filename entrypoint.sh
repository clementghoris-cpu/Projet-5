#!/bin/sh
set -e # s'arrête immédiatement si une commande échoue

echo "Initialisation de la base de données..."
uv run python src/database/init_db.py

echo "Démarrage de l'API..."
exec uv run uvicorn src.api.main:app --host 0.0.0.0 --port 10000
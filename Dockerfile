FROM python:3.14-slim

# Installation du package manager uv directement depuis le binaire officiel
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Configuration de l'utilisateur non-root (requis par Render)
# Utilisation de l'utilisateur root dans l'environnement de développement (override du fichier docker-compose.test.yml)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=/home/user/app

WORKDIR $HOME/app

COPY --chown=user pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-dev --no-install-project

COPY --chown=user src/ ./src/
COPY --chown=user data/ ./data/
# l'ajout de * permet d'éviter que le déploiement n'échoue car il ne va pas trouver le fichier .env dans l'environnement staging ou production
COPY --chown=user .env* .

RUN uv sync --frozen --no-cache --no-dev

COPY --chown=user --chmod=755 entrypoint.sh ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
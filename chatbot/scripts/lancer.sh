#!/usr/bin/env bash
# Lance la passerelle (lecture seule) puis le chatbot. Usage : scripts/lancer.sh   (ANTHROPIC_API_KEY optionnelle)
# Défense en profondeur : le code du modèle est mis en lecture seule pour l'utilisateur courant avant le lancement,
# et Python n'écrit pas de fichiers .pyc. (Sous root, chmod n'empêche pas l'écriture : lancer en utilisateur normal.)
set -euo pipefail
cd "$(dirname "$0")/.."
git submodule update --init vendor/hackathon_acces_soins
chmod -R a-w vendor/hackathon_acces_soins
export PYTHONDONTWRITEBYTECODE=1
uv run python -m passerelle.server 8770 &
PASS=$!
trap 'kill $PASS 2>/dev/null' EXIT
until curl -sf http://127.0.0.1:8770/v1/sante >/dev/null; do sleep 1; done
uv run python -m chat.server 8768

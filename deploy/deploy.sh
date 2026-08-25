#!/usr/bin/env bash
# Run this ON THE VPS (not from this session — see README for why) to deploy
# or update Khanh Voice. Requires Docker + the Docker Compose plugin installed,
# and a .env file at the repo root (copy .env.example and fill in real values).
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "Missing .env — copy .env.example to .env and fill in real values first." >&2
  exit 1
fi

git pull --ff-only
docker compose -f deploy/docker-compose.yml build
docker compose -f deploy/docker-compose.yml up -d

echo "Deployed. Check logs with: docker compose -f deploy/docker-compose.yml logs -f"

#!/usr/bin/env bash
set -euo pipefail
URL="${1:-http://localhost:8000/health}"

if curl --fail --silent "$URL" | grep -q '"status":"ok"'; then
  echo "healthy"
  exit 0
fi

echo "unhealthy"
exit 1

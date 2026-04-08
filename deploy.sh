#!/usr/bin/env bash
set -euo pipefail

HOST="expense-tracker.local"

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()    { echo -e "${GREEN}==>${NC} $*"; }
warn()    { echo -e "${YELLOW}[warn]${NC} $*"; }
die()     { echo -e "${RED}[error]${NC} $*" >&2; exit 1; }

# ── Prerequisites ─────────────────────────────────────────────────────────────
for cmd in minikube kubectl docker; do
  command -v "$cmd" &>/dev/null || die "'$cmd' is not installed"
done

# ── Minikube ──────────────────────────────────────────────────────────────────
info "Checking minikube..."
if ! minikube status --format='{{.Host}}' 2>/dev/null | grep -q "Running"; then
  info "Starting minikube..."
  minikube start
fi

info "Enabling ingress addon..."
minikube addons enable ingress

# ── Build images inside minikube's Docker daemon ──────────────────────────────
info "Pointing Docker at minikube's daemon..."
eval "$(minikube docker-env)"

info "Building backend image..."
docker build -t expense-tracker-backend:latest ./backend

info "Building frontend image..."
docker build -t expense-tracker-frontend:latest ./frontend

# ── Deploy ────────────────────────────────────────────────────────────────────
info "Applying Kubernetes manifests..."
kubectl apply -f k8s/

# ── /etc/hosts ────────────────────────────────────────────────────────────────
MINIKUBE_IP=$(minikube ip)
if grep -qF "$HOST" /etc/hosts 2>/dev/null; then
  warn "/etc/hosts already has an entry for $HOST — skipping (update manually if the IP changed)"
else
  info "Adding $MINIKUBE_IP $HOST to /etc/hosts (requires sudo)..."
  echo "$MINIKUBE_IP $HOST" | sudo tee -a /etc/hosts > /dev/null
fi

# ── Wait for rollout ──────────────────────────────────────────────────────────
info "Waiting for deployments to be ready..."
kubectl rollout status deployment/postgres --timeout=120s
kubectl rollout status deployment/backend  --timeout=120s
kubectl rollout status deployment/frontend --timeout=120s

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}Deployed!${NC} Open http://$HOST"

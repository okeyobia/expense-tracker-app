# Kubernetes Quick Start (Minikube)

## Prerequisites

Install the following before proceeding:

| Tool | Install |
|------|---------|
| [Docker](https://docs.docker.com/get-docker/) | Required to build images |
| [minikube](https://minikube.sigs.k8s.io/docs/start/) | Local Kubernetes cluster |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | Kubernetes CLI |

Verify everything is installed:

```bash
docker --version
minikube version
kubectl version --client
```

---

## Option A — Automated (recommended)

Run the deploy script from the project root:

```bash
./deploy.sh
```

This handles everything: starts minikube, builds images, applies manifests, patches `/etc/hosts`, and waits for pods to be ready.

Skip to [Verify the deployment](#verify-the-deployment) when it finishes.

---

## Option B — Manual step by step

### 1. Start minikube

```bash
minikube start
minikube addons enable ingress
```

### 2. Build images inside minikube

Point your shell at minikube's Docker daemon so images are available to the cluster without a registry:

```bash
eval $(minikube docker-env)
```

> Run this in every new terminal session you use for building.

Build both images:

```bash
docker build -t expense-tracker-backend:latest ./backend
docker build -t expense-tracker-frontend:latest ./frontend
```

### 3. (Optional) Update secrets

The default secrets use `postgres` as the DB password and `change-me-in-production` as the JWT secret. To use your own values, edit `k8s/secret.yaml` before applying:

```bash
echo -n "your-password" | base64   # replace postgres-password
echo -n "your-jwt-secret" | base64 # replace jwt-secret
```

Also update `database-url` if you change the DB password:

```bash
echo -n "postgresql://postgres:your-password@postgres/expense_tracker" | base64
```

### 4. Apply manifests

```bash
kubectl apply -f k8s/
```

### 5. Add host entry

```bash
echo "$(minikube ip) expense-tracker.local" | sudo tee -a /etc/hosts
```

### 6. Wait for pods

```bash
kubectl rollout status deployment/postgres
kubectl rollout status deployment/backend
kubectl rollout status deployment/frontend
```

---

## Verify the deployment

Check all pods are running:

```bash
kubectl get pods
```

Expected output:

```
NAME                        READY   STATUS    RESTARTS   AGE
postgres-xxxxxxxxx-xxxxx    1/1     Running   0          1m
backend-xxxxxxxxx-xxxxx     1/1     Running   0          1m
frontend-xxxxxxxxx-xxxxx    1/1     Running   0          1m
```

Open the app:

```bash
open http://expense-tracker.local
```

---

## Useful commands

```bash
# Stream logs from a service
kubectl logs -f deployment/backend
kubectl logs -f deployment/frontend

# Describe a pod (useful for debugging crash loops)
kubectl describe pod -l app=backend

# Open a shell in the backend container
kubectl exec -it deployment/backend -- bash

# Connect to the database
kubectl exec -it deployment/postgres -- psql -U postgres expense_tracker

# Restart a deployment after rebuilding an image
kubectl rollout restart deployment/backend

# Tear everything down
kubectl delete -f k8s/
```

---

## Rebuilding after code changes

```bash
# Re-point Docker at minikube (if in a new terminal)
eval $(minikube docker-env)

# Rebuild the changed image
docker build -t expense-tracker-backend:latest ./backend  # or frontend

# Trigger a fresh rollout
kubectl rollout restart deployment/backend  # or frontend
```

---

## Troubleshooting

**Pods stuck in `Pending`**
- Run `kubectl describe pod <pod-name>` and check the Events section.
- Usually a resource constraint — try `minikube start --memory=4096`.

**`ImagePullBackOff` or `ErrImageNeverPull`**
- The image was not built inside minikube's Docker daemon.
- Run `eval $(minikube docker-env)` and rebuild.

**Backend `CrashLoopBackOff`**
- Postgres may not be ready yet. Check with `kubectl logs deployment/backend`.
- Run `kubectl rollout restart deployment/backend` once postgres is healthy.

**`expense-tracker.local` not resolving**
- Confirm the entry exists: `grep expense-tracker /etc/hosts`
- If missing: `echo "$(minikube ip) expense-tracker.local" | sudo tee -a /etc/hosts`
- If minikube's IP changed after a restart, update the existing entry manually.

**Ingress returns 404**
- The ingress controller may still be starting. Wait 60 seconds and retry.
- Check: `kubectl get pods -n ingress-nginx`

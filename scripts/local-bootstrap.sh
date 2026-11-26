#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-devsecops-demo}"
IMAGE_TAG="${IMAGE_TAG:-ghcr.io/lampreave/devsecops-gitops-platform/demo-service:1.0.0}"

for cmd in docker kind kubectl helm; do
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "Error: required tool '${cmd}' is not installed." >&2
    exit 1
  fi
done

echo "==> 1. Building demo-service container image locally..."
docker build -t "${IMAGE_TAG}" -f app/Dockerfile app

echo "==> 2. Creating kind cluster '${CLUSTER_NAME}' (if not present)..."
if ! kind get clusters | grep -qx "${CLUSTER_NAME}"; then
  kind create cluster --name "${CLUSTER_NAME}"
fi

echo "==> 3. Loading local image into kind cluster..."
kind load docker-image "${IMAGE_TAG}" --name "${CLUSTER_NAME}"

echo "==> 4. Installing ArgoCD..."
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=180s

echo "==> 5. Applying ArgoCD AppProject & Root App-of-Apps..."
kubectl apply -f gitops/argocd/projects/platform-project.yaml
kubectl apply -f gitops/argocd/root-app.yaml

echo "==> Done! Access ArgoCD UI with:"
echo "    kubectl port-forward svc/argocd-server -n argocd 8443:443"

# ADR-002: Pull-Based GitOps Delivery with ArgoCD

- **Status:** Accepted
- **Date:** 2026-11-26

## Context

Push-based CI deployments (`kubectl apply` or `helm upgrade` directly from CI runners) require giving external CI runners broad cluster credentials and allow configuration drift when manual changes occur inside Kubernetes clusters.

## Decision

Adopt pull-based GitOps using ArgoCD with an `AppProject` boundary, an App-of-Apps root manifest (`gitops/argocd/root-app.yaml`), and a multi-environment `ApplicationSet`:

- **`dev` environment:** Automated sync with `prune: true` and `selfHeal: true` for rapid developer feedback.
- **`prod` environment:** Manual sync gate so promotions remain auditable and intentional.

## Consequences

- **Positive:** Zero Kubernetes admin credentials stored in CI; Git commit history serves as the complete audit trail; accidental drift in `dev` self-heals automatically.
- **Trade-off:** Teams must make all cluster configuration changes via Git PRs rather than ad-hoc `kubectl edit`.

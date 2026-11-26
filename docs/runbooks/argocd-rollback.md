# Runbook: Zero-Downtime Rollback with ArgoCD

## Trigger
`DemoServiceHighErrorRate` fires in Prometheus/Alertmanager, or a production deployment shows elevated latency/errors after sync.

## Immediate Mitigation (< 2 minutes)

1. **Confirm current revision and health:**
   ```bash
   argocd app get demo-service-prod
   argocd app history demo-service-prod
   ```
2. **Perform an immediate ArgoCD rollback (emergency stabilization):**
   ```bash
   argocd app rollback demo-service-prod <PREVIOUS_HEALTHY_ID>
   ```
3. **Reconcile Git state (prevent drift on next sync):**
   - Revert the offending commit in Git (`git revert <bad-sha>`) and merge via expedited PR so Git remains the single source of truth.
4. **Verify recovery:**
   - Check `/healthz`, `/readyz`, and Prometheus `demo_service_http_requests_total` 5xx rate returns to `0%`.
   - Open a blameless post-incident review noting root cause and any missing CI/DAST check.

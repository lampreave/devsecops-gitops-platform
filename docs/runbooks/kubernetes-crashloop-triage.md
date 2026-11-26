# Runbook: Kubernetes Pod CrashLoopBackOff Triage

## Trigger
`DemoServicePodCrashLooping` alert fires or `kubectl get pods -n demo-prod` shows `CrashLoopBackOff` / repeated restarts.

## Diagnostic Checklist

1. **Inspect Pod events & exit codes:**
   ```bash
   kubectl describe pod -n demo-prod -l app.kubernetes.io/name=demo-service
   ```
   - Look for `OOMKilled` (exit code `137` -> review memory limits in `values-prod.yaml`), `ImagePullBackOff` (check GHCR image tag/pull secret), or failed `livenessProbe`/`readinessProbe`.
2. **Check previous container logs:**
   ```bash
   kubectl logs -n demo-prod -l app.kubernetes.io/name=demo-service --previous --tail=100
   ```
3. **Verify read-only root filesystem & non-root compatibility:**
   - Confirm the new release does not attempt to write outside `/tmp` or bind to privileged ports (`< 1024`), since the Helm chart enforces `readOnlyRootFilesystem: true` and `runAsUser: 10001`.
4. **Verify NetworkPolicy & DNS:**
   - Confirm ingress traffic comes from the allowed namespace selector and egress DNS (`kube-system:53`) is reachable.
5. **Escalate or Roll Back:**
   - If the issue followed a recent deploy, follow `docs/runbooks/argocd-rollback.md` first, then reproduce locally with `scripts/local-bootstrap.sh`.

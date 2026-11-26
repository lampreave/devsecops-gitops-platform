# ADR-001: Branch-Policy Build-Blocking Security Gates

- **Status:** Accepted
- **Date:** 2026-11-26

## Context

Blocking every developer commit with noisy, unfixable vulnerability findings causes alert fatigue and drives teams to bypass CI checks. Conversely, purely advisory scanning lets critical container CVEs and hardcoded secrets reach production.

## Decision

Implement parameterized, reusable GitHub Actions workflows (`reusable-devsecops-ci.yml`) enforcing two tiers:

1. **Always blocking (all branches):** Secret scanning (`Gitleaks`), Dockerfile linting (`Hadolint`), unit tests, and IaC/Kubernetes schema validation (`helm lint`, `kubeconform`, `terraform validate`).
2. **Branch-policy CVE gate (`Trivy`):** Filter to fixable vulnerabilities (`ignore-unfixed: true`) of `HIGH`/`CRITICAL` severity. Enforce build-blocking (`exit-code: 1`) on `main` and release PRs, while allowing teams to run in advisory mode (`block_on_vulnerabilities: false`) on early experimental branches.

## Consequences

- **Positive:** Prevents leaked credentials and fixable high-severity CVEs from reaching container registries without breaking builds over upstream OS packages with no patch available.
- **Trade-off:** Requires periodic base-image refreshes and clear CVE triage ownership (documented in `docs/runbooks/cve-remediation.md`).

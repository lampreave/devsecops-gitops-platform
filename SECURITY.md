# Security Policy

## Scope

This repository is a reference DevSecOps and GitOps platform demonstrating secure CI/CD workflows, container hardening, Kubernetes policy defaults, Infrastructure as Code security checks, and operational runbooks. All code, configurations, and sample workloads are 100% synthetic and contain no proprietary employer data or live credentials.

## Built-In Security Controls

- **Secret Scanning:** Gitleaks runs on every pull request and push to prevent credential leaks.
- **Container Hardening:** Multi-stage Dockerfiles run as non-root (`UID 10001`), drop all Linux capabilities, enforce a read-only root filesystem, and are linted with Hadolint.
- **Supply Chain & Vulnerability Gates:** Syft generates CycloneDX SBOMs; Trivy enforces branch-aware vulnerability gates (advisory on feature branches, build-blocking for fixable `HIGH`/`CRITICAL` CVEs on `main`).
- **Dynamic Testing (DAST):** OWASP ZAP Baseline scans the running demo service in CI.
- **IaC & Manifest Validation:** Helm charts, Kubernetes manifests, and Terraform modules are validated with `helm lint`, `kubeconform`, `terraform validate`, and `trivy config`.
- **Keyless Cloud Auth:** Terraform IAM modules enforce GitHub Actions OIDC federation rather than static cloud access keys.

## Reporting a Vulnerability

If you spot a security issue or misconfiguration in this reference repository, please open a GitHub Security Advisory or issue on `lampreave/devsecops-gitops-platform`.

# ADR-003: Keyless Cloud Authentication via GitHub Actions OIDC

- **Status:** Accepted
- **Date:** 2026-11-26

## Context

Long-lived IAM user access keys stored in CI secrets create high-impact compromise risk and ongoing rotation overhead.

## Decision

Provision AWS IAM roles using GitHub Actions OpenID Connect (OIDC) federation (`infra/terraform/modules/github-oidc-ecr/`), restricting `AssumeRoleWithWebIdentity` strictly by:

- Audience (`sts.amazonaws.com`)
- Exact repository and branch subject claim (`repo:lampreave/devsecops-gitops-platform:ref:refs/heads/main`)
- Scoped write permissions limited to a single KMS-encrypted, immutable ECR repository.

## Consequences

- **Positive:** Eliminates static AWS credentials in GitHub Secrets; tokens expire automatically within one hour; every assume-role call is traceable to a specific repository and branch in AWS CloudTrail.
- **Trade-off:** Requires configuring the OIDC identity provider once per AWS account.

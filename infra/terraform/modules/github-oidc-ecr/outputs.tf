output "ecr_repository_url" {
  description = "URI of the KMS-encrypted ECR repository."
  value       = aws_ecr_repository.service.repository_url
}

output "github_ci_role_arn" {
  description = "IAM role ARN assumed by GitHub Actions via keyless OIDC."
  value       = aws_iam_role.github_ci.arn
}

output "kms_key_arn" {
  description = "ARN of the KMS CMK encrypting container images."
  value       = aws_kms_key.ecr.arn
}

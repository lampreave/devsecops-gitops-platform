data "aws_caller_identity" "current" {}

resource "aws_kms_key" "ecr" {
  description             = "KMS key for ${var.project_name}-${var.environment} ECR image encryption"
  deletion_window_in_days = 14
  enable_key_rotation     = true

  tags = var.tags
}

resource "aws_kms_alias" "ecr" {
  name          = "alias/${var.project_name}-${var.environment}-ecr"
  target_key_id = aws_kms_key.ecr.key_id
}

resource "aws_ecr_repository" "service" {
  name                 = "${var.project_name}/${var.environment}/${var.service_name}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.ecr.arn
  }

  tags = var.tags
}

resource "aws_ecr_lifecycle_policy" "service" {
  repository = aws_ecr_repository.service.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Retain last ${var.max_image_count} tagged container images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = var.max_image_count
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

resource "aws_iam_openid_connect_provider" "github" {
  count = var.create_oidc_provider ? 1 : 0

  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]

  tags = var.tags
}

locals {
  oidc_provider_arn = var.create_oidc_provider ? aws_iam_openid_connect_provider.github[0].arn : "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/token.actions.githubusercontent.com"
}

data "aws_iam_policy_document" "github_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [local.oidc_provider_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repository}:ref:refs/heads/${var.allowed_branch}"]
    }
  }
}

resource "aws_iam_role" "github_ci" {
  name                 = "${var.project_name}-${var.environment}-github-ci"
  assume_role_policy   = data.aws_iam_policy_document.github_assume_role.json
  max_session_duration = 3600

  tags = var.tags
}

data "aws_iam_policy_document" "ecr_push" {
  statement {
    sid     = "ECRAuthToken"
    effect  = "Allow"
    actions = ["ecr:GetAuthorizationToken"]
    # trivy:ignore:AVD-AWS-0057 AWS API requires '*' for ecr:GetAuthorizationToken
    resources = ["*"]
  }

  statement {
    sid    = "ScopedRepositoryPush"
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
    ]
    resources = [aws_ecr_repository.service.arn]
  }
}

resource "aws_iam_role_policy" "ecr_push" {
  name   = "scoped-ecr-push"
  role   = aws_iam_role.github_ci.id
  policy = data.aws_iam_policy_document.ecr_push.json
}

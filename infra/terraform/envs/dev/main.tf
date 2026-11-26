terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.70"
    }
  }
}

provider "aws" {
  region = "ca-central-1"
}

module "github_oidc_ecr" {
  source = "../../modules/github-oidc-ecr"

  project_name      = "devsecops-platform"
  environment       = "dev"
  service_name      = "demo-service"
  github_repository = "lampreave/devsecops-gitops-platform"
  allowed_branch    = "main"
  max_image_count   = 15

  tags = {
    Project     = "devsecops-gitops-platform"
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

variable "project_name" {
  description = "Short platform identifier used as resource prefix."
  type        = string
}

variable "environment" {
  description = "Target deployment environment (dev or prod)."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "service_name" {
  description = "Name of the containerized service."
  type        = string
}

variable "github_repository" {
  description = "GitHub repository in owner/repo format allowed to assume the OIDC role."
  type        = string
}

variable "allowed_branch" {
  description = "Git branch allowed to assume the CI deployment role."
  type        = string
  default     = "main"
}

variable "create_oidc_provider" {
  description = "Whether to create the GitHub OIDC provider in this AWS account."
  type        = bool
  default     = true
}

variable "max_image_count" {
  description = "Maximum number of container images retained in ECR."
  type        = number
  default     = 20
}

variable "tags" {
  description = "Common resource tags."
  type        = map(string)
  default     = {}
}

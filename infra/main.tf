terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# "provider" = com qual nuvem o Terraform fala.
provider "aws" {
  region = var.aws_region
}

# ---- variáveis de entrada ----
variable "aws_region" {
  description = "Região da AWS"
  type        = string
  default     = "sa-east-1"
}

variable "nome_repositorio" {
  description = "Nome do repositório de imagens"
  type        = string
  default     = "tarefas-api"
}

# ---- o recurso: um repositório ECR ----
resource "aws_ecr_repository" "app" {
  name                 = var.nome_repositorio
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# ---- saída: a URL, pra usar no "docker push" ----
output "url_repositorio" {
  description = "Endereço do repositório ECR"
  value       = aws_ecr_repository.app.repository_url
}
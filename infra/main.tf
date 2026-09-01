# ============================================================
# main.tf — Infraestrutura AWS para o fastapi-py
#
# Cria: 1 repositório ECR + 1 role IAM + 1 Security Group + 1 EC2 t3.micro
#       rodando Amazon Linux 2023 com Docker instalado.
#
# Fluxo: Terraform cria a infra -> push da imagem pro ECR ->
#        SSH na EC2 -> "docker compose up" (API + Postgres em containers).
# ============================================================

terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # O "state" (o que o Terraform já criou) fica num bucket S3, não na máquina.
  # ATENÇÃO: este bucket precisa JÁ EXISTIR antes do "terraform init".
  backend "s3" {
    bucket       = "terraform-state-ghsoftware"
    key          = "fastapi/terraform.tfstate"
    region       = "us-east-2"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = var.aws_region
}

# ------------------------------------------------------------
# Variáveis
# ------------------------------------------------------------

variable "aws_region" {
  description = "Região onde a infraestrutura roda"
  type        = string
  default     = "us-west-2"
}

variable "project" {
  description = "Nome usado em tags e nomes de recurso"
  type        = string
  default     = "fastapi-py"
}

variable "ssh_key_name" {
  description = "Nome de um Key Pair que já existe no AWS (para SSH)"
  type        = string
  default     = "chave-fastapi-prod"
}

variable "my_ip_cidr" {
  description = "Meu IP público /32 — único que pode fazer SSH"
  type        = string
  default     = "186.204.240.227/32"
}

locals {
  tags = {
    Project     = var.project
    Provisioned = "Terraform"
    Cliente     = "Guilherme"
  }
}

# ------------------------------------------------------------
# Data sources — buscam o que já existe na AWS
# ------------------------------------------------------------

# AMI mais recente do Amazon Linux 2023.
data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

# VPC padrão da conta.
data "aws_vpc" "default" {
  default = true
}

# Subnets dessa VPC.
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# ------------------------------------------------------------
# ECR — repositório da imagem Docker da API
# ------------------------------------------------------------

resource "aws_ecr_repository" "api" {
  name                 = "${var.project}-prod"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.tags
}

# ------------------------------------------------------------
# IAM — permissão da EC2 para puxar a imagem do ECR
# role (o "cargo") + instance profile (o "crachá" que a EC2 veste)
# ------------------------------------------------------------

resource "aws_iam_role" "ec2" {
  name = "${var.project}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })

  tags = local.tags
}

# Leitura no ECR.
resource "aws_iam_role_policy_attachment" "ecr_read" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# Acesso via SSM Session Manager (sem chave SSH, sem porta 22 aberta).
resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ec2" {
  name = "${var.project}-ec2-profile"
  role = aws_iam_role.ec2.name
}

# ------------------------------------------------------------
# Security Group — firewall da EC2
# ------------------------------------------------------------

resource "aws_security_group" "api" {
  name        = "${var.project}-sg"
  description = "Firewall da EC2 do ${var.project}"
  vpc_id      = data.aws_vpc.default.id
  tags        = local.tags
}

resource "aws_vpc_security_group_ingress_rule" "ssh" {
  security_group_id = aws_security_group.api.id
  description       = "SSH so do meu IP"
  cidr_ipv4         = var.my_ip_cidr
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.api.id
  description       = "HTTP publico"
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "https" {
  security_group_id = aws_security_group.api.id
  description       = "HTTPS publico"
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "all_outbound" {
  security_group_id = aws_security_group.api.id
  description       = "Saida liberada"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

# ------------------------------------------------------------
# EC2 — servidor que roda a aplicação
# ------------------------------------------------------------

resource "aws_instance" "api" {
  ami                         = data.aws_ami.al2023.id
  instance_type               = "t3.micro"
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.api.id]
  iam_instance_profile        = aws_iam_instance_profile.ec2.name
  key_name                    = var.ssh_key_name
  associate_public_ip_address = true

    # IMDSv2 obrigatório (protege as credenciais da instância contra SSRF)
  metadata_options {
    http_tokens   = "required"
    http_endpoint = "enabled"
  }

  # 20 GB (o padrão de 8 GB fica apertado com imagens + Postgres).
  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  # Roda uma vez no primeiro boot: instala Docker + plugin do compose.
  # O deploy do app (docker compose up) e feito depois, via SSH.
  user_data = <<-EOT
    #!/bin/bash
    set -e
    dnf update -y
    dnf install -y docker
    systemctl enable --now docker
    usermod -aG docker ec2-user

    mkdir -p /usr/local/lib/docker/cli-plugins
    curl -sSL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
      -o /usr/local/lib/docker/cli-plugins/docker-compose
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
  EOT

  tags = merge(local.tags, { Name = "${var.project}-server" })
}

# ------------------------------------------------------------
# Outputs
# ------------------------------------------------------------

output "ecr_repository_url" {
  description = "URL do ECR (usar no docker tag/push)"
  value       = aws_ecr_repository.api.repository_url
}

output "ec2_public_ip" {
  description = "IP publico da EC2"
  value       = aws_instance.api.public_ip
}

output "ssh_command" {
  description = "Comando pronto pra conectar"
  value       = "ssh -i ~/.ssh/${var.ssh_key_name}.pem ec2-user@${aws_instance.api.public_ip}"
}

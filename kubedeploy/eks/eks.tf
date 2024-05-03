provider "aws" {
  region = var.region
}

variable "cluster_name" {
  type    = string
  default = "cwad-cluster"
}

variable "vpc_name" {
  type    = string
  default = "cwad-vpc"
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.10.0.0/16"
}

variable "vpc_azs" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b"]
}

variable "subnets" {
  type = map(list(string))
  default = {
    "public_subnets"  = ["10.10.1.0/24", "10.10.2.0/24"],
    "private_subnets" = ["10.10.3.0/24", "10.10.4.0/24"],
    "intra_subnets"   = ["10.10.5.0/24", "10.10.6.0/24"]
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 4.0"

  name = var.vpc_name
  cidr = var.vpc_cidr

  azs             = var.vpc_azs
  private_subnets = var.subnets.private_subnets
  public_subnets  = var.subnets.public_subnets
  intra_subnets   = var.subnets.intra_subnets

  enable_nat_gateway = true

  public_subnet_tags = {
    "kubernetes.io/role/elb" = 1
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = 1
  }
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.15.1"

  cluster_name                   = var.cluster_name
  cluster_endpoint_public_access = true

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
  }

  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.intra_subnets

  # EKS Managed Node Group(s)
  eks_managed_node_group_defaults = {
    ami_type       = "AL2_x86_64"
    instance_types = ["m5.large"]

    attach_cluster_primary_security_group = true
  }
  node_security_group_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = null
  }

  eks_managed_node_groups = {
    ascode-cluster-wg = {
      min_size     = 1
      max_size     = 2
      desired_size = 1

      instance_types = ["m5.large"]
      capacity_type  = "ON_DEMAND"


    }
  }

}


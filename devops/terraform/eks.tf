data "aws_eks_cluster" "eks_fivessun" {
  name = module.eks_fivessun_1_27.cluster_name
}

data "aws_eks_cluster_auth" "eks_fivessun" {
  name = module.eks_fivessun_1_27.cluster_name
}

data "aws_ami" "eks_bottlerocket_1_27" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["bottlerocket-aws-k8s-1.27-aarch64-*"]
  }
}

provider "kubernetes" {
  alias = "fivessun"
  host  = data.aws_eks_cluster.eks_fivessun.endpoint
  token = data.aws_eks_cluster_auth.eks_fivessun.token

  cluster_ca_certificate = base64decode(data.aws_eks_cluster.eks_fivessun.certificate_authority[0].data)
}

module "eks_fivessun_1_27" {
  providers = {
    kubernetes = kubernetes.fivessun
  }

  source  = "terraform-aws-modules/eks/aws"
  version = "19.16.0"

  cluster_name                           = local.eks_cluster_name
  cluster_version                        = "1.27"
  cluster_enabled_log_types              = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
  cloudwatch_log_group_retention_in_days = 7

  kms_key_owners = [
    "arn:aws:iam::629484894158:role/aws-reserved/sso.amazonaws.com/ap-northeast-2/AWSReservedSSO_AdministratorAccess_0e015edc8df69a93",
  ]

  cluster_additional_security_group_ids = [aws_security_group.app_mesh.id]
  cluster_security_group_additional_rules = {
    ingress_infra = {
      protocol    = -1
      from_port   = 0
      to_port     = 0
      cidr_blocks = ["10.0.0.0/16"]
      type        = "ingress"
    }
  }

  cluster_endpoint_private_access = true
  cluster_endpoint_public_access  = false

  iam_role_name            = "fivessun-eks-role"
  iam_role_use_name_prefix = true

  cluster_addons = {
    coredns = {
      resolve_conflicts = "OVERWRITE"
      addon_version     = "v1.10.1-eksbuild.2"
    }
    kube-proxy = {
      resolve_conflicts = "OVERWRITE"
      addon_version     = "v1.27.4-eksbuild.2"
    }
    vpc-cni = {
      resolve_conflicts = "OVERWRITE"
      addon_version     = "v1.13.4-eksbuild.1"
    }
    aws-ebs-csi-driver = {
      resolve_conflicts = "OVERWRITE"
    }
  }

  vpc_id     = module.vpc.vpc_id
  subnet_ids = concat(module.vpc.private_subnets, module.vpc.public_subnets)


  eks_managed_node_group_defaults = {
    ami_id                 = data.aws_ami.eks_bottlerocket_1_27.id
    platform               = "bottlerocket"
    disk_size              = 20
    capacity_type          = "SPOT"
    vpc_security_group_ids = [aws_security_group.app_mesh.id]

    enable_bootstrap_user_data = true
  }

  eks_managed_node_groups = {
    default = {
      min_size     = 1
      max_size     = 2
      desired_size = 1
      instance_types = [
        "t4g.small",
        "t4g.medium",
      ]
      capacity_type = "SPOT"

      name            = "default-ng"
      use_name_prefix = true

      labels = {
        compute-type = "managed-nodegroup"
        nodegroup    = "default"
      }

      update_config = {
        max_unavailable_percentage = 50
      }
      subnet_ids = module.vpc.private_subnets

      iam_role_additional_policies = {
        # Required by EBS CSI Driver
        AmazonEBSCSIDriverPolicy = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy",
        # Required by Karpenter
        AmazonSSMManagedInstanceCore = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
      }
    }
  }
  manage_aws_auth_configmap = true

  aws_auth_roles = [
    {
      rolearn  = "arn:aws:iam::629484894158:role/AWSReservedSSO_AdministratorAccess_0e015edc8df69a93"
      username = "{{SessionName}}"
      groups   = ["system:masters"]
    },
  ]

  fargate_profiles = {
    default = {
      name = "default"
      selectors = [
        for ns in [
          "default",
          #          "keda",
          "kube-system",
          "karpenter"
        ] :
        {
          namespace = ns
          labels = {
            "eks/fargate-profile" = "default"
          }
        }
      ]
      subnet_ids = module.vpc.private_subnets
    }
  }

  enable_irsa = true

  tags = {
    # Tag node group resources for Karpenter auto-discovery
    # NOTE - if creating multiple security groups with this module, only tag the
    # security group that Karpenter should utilize with the following tag
    "karpenter.sh/discovery/${local.eks_cluster_name}" = "-"
  }
}

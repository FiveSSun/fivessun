module "vpc_cni_ipv4_irsa_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5"

  role_name             = "eks-vpc-cni-ipv4-role"
  attach_vpc_cni_policy = true
  vpc_cni_enable_ipv4   = true

  oidc_providers = {
    prod = {
      provider_arn               = module.eks_fivessun_1_27.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-node"]
    }
  }
}

module "ebs_csi_irsa_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5"

  role_name             = "eks-ebs-csi-role"
  attach_ebs_csi_policy = true

  oidc_providers = {
    prod = {
      provider_arn               = module.eks_fivessun_1_27.oidc_provider_arn
      namespace_service_accounts = ["kube-system:ebs-csi-controller-sa"]
    }
  }
}

module "karpenter_controller_irsa_role" {
  source    = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version   = "~> 5"
  role_name = "eks-karpenter-controller"

  oidc_providers = {
    prod = {
      provider_arn               = module.eks_fivessun_1_27.oidc_provider_arn
      namespace_service_accounts = ["karpenter:karpenter"]
    }
  }

  role_policy_arns = {
    ec2 = data.aws_iam_policy.ec2_full_access.arn
    eks = aws_iam_policy.karpenter_controller.arn
    ssm = data.aws_iam_policy.external_secrets_ssm_irsa.arn
  }
}

module "external_secrets_irsa_role" {
  source    = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version   = "~> 5"
  role_name = "eks-external-secrets"

  oidc_providers = {
    prod = {
      provider_arn               = module.eks_fivessun_1_27.oidc_provider_arn
      namespace_service_accounts = ["external-secrets:external-secrets"]
    }
  }

  role_policy_arns = {
    default = data.aws_iam_policy.external_secrets_secret_manager_irsa.arn
    ssm     = data.aws_iam_policy.external_secrets_ssm_irsa.arn
  }
}

module "fivessun-serviceaccounts" {
  source    = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version   = "~> 5"
  role_name = "fivessun-serviceaccounts"

  assume_role_condition_test = "StringLike"

  oidc_providers = {
    prod = {
      provider_arn               = module.eks_fivessun_1_27.oidc_provider_arn
      namespace_service_accounts = ["*:*"]
    }
  }

  role_policy_arns = {
    s3_policy  = data.aws_iam_policy.s3_full_access.arn
    ecr_policy = data.aws_iam_policy.ecr_read_only_access.arn
  }
}

data "aws_iam_policy" "ec2_full_access" {
  name = "AmazonEC2FullAccess"
}

data "aws_iam_policy" "ecr_read_only_access" {
  name = "AmazonEC2ContainerRegistryReadOnly"
}

data "aws_iam_policy" "external_secrets_secret_manager_irsa" {
  name = "SecretsManagerReadWrite"
}

data "aws_iam_policy" "external_secrets_ssm_irsa" {
  name = "AmazonSSMReadOnlyAccess"
}

data "aws_iam_policy" "s3_full_access" {
  name = "AmazonS3FullAccess"
}

resource "aws_iam_policy" "karpenter_controller" {
  name   = "karpenter_controller"
  policy = data.aws_iam_policy_document.karpenter_controller.json
}

data "aws_iam_policy_document" "karpenter_controller" {
  statement {
    effect = "Allow"
    actions = [
      "eks:DescribeCluster",
    ]
    resources = [
      module.eks_fivessun_1_27.cluster_arn,
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "pricing:GetProducts",
      "ec2:DescribeSubnets",
      "ec2:DescribeSpotPriceHistory",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeLaunchTemplates",
      "ec2:DescribeInstances",
      "ec2:DescribeInstanceTypes",
      "ec2:DescribeInstanceTypeOfferings",
      "ec2:DescribeImages",
      "ec2:DescribeAvailabilityZones",
      "ec2:CreateTags",
      "ec2:CreateLaunchTemplate",
      "ec2:CreateFleet",
    ]
    resources = [
      "*",
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "ec2:TerminateInstances",
      "ec2:DeleteLaunchTemplate",
    ]
    condition {
      test     = "StringEquals"
      values   = ["ec2:ResourceTag/karpenter.sh/discovery"]
      variable = module.eks_fivessun_1_27.cluster_name
    }
    resources = [
      "*",
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "ec2:RunInstaces",
    ]
    condition {
      test     = "StringEquals"
      values   = ["ec2:ResourceTag/karpenter.sh/discovery"]
      variable = module.eks_fivessun_1_27.cluster_name
    }
    resources = [
      "arn:aws:ec2:*:629484894158:launch-template/*",
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "ec2:RunInstaces",
    ]
    resources = [
      "arn:aws:ec2:*::image/*",
      "arn:aws:ec2:*:629484894158:volume/*",
      "arn:aws:ec2:*:629484894158:subnet/*",
      "arn:aws:ec2:*:629484894158:spot-instances-request/*",
      "arn:aws:ec2:*:629484894158:security-group/*",
      "arn:aws:ec2:*:629484894158:network-interface/*",
      "arn:aws:ec2:*:629484894158:instance/*",
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "ssm:GetParameter",
    ]
    resources = [
      "arn:aws:ssm:*:*:parameter/aws/service/*",
      "arn:aws:ssm:ap-northeast-2::parameter/aws/service/*",
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "iam:PassRole",
    ]
    resources = [
      "arn:aws:iam::629484894158:role/default-ng-eks-node-group-20230906061531551300000005",
    ]
  }
}

resource "aws_iam_instance_profile" "karpenter_default_1_27" {
  name = "eks-karpenter-${local.eks_cluster_name}-default"
  role = module.eks_fivessun_1_27.eks_managed_node_groups["default"].iam_role_name
}

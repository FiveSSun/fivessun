module "vpc" {
  source  = "registry.terraform.io/terraform-aws-modules/vpc/aws"
  version = "5.0.0"
  name    = "fivessun"
  cidr    = "10.0.0.0/16"

  enable_nat_gateway            = true
  enable_dns_hostnames          = true
  manage_default_route_table    = false
  manage_default_network_acl    = false
  manage_default_security_group = false
  manage_default_vpc            = false
  single_nat_gateway            = true # If false, one NAT gateway per AZ will be created

  azs = [
    "ap-northeast-2a",
    "ap-northeast-2b",
  ]

  public_subnets = [
    "10.0.0.0/22",
    "10.0.4.0/22",
  ]

  private_subnets = [
    "10.0.100.0/22",
    "10.0.104.0/22",
  ]

  public_subnet_tags = {
    "kubernetes.io/cluster/${local.eks_cluster_name}" = "shared"
    "kubernetes.io/role/elb"                          = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb"                  = "1"
    "kubernetes.io/cluster/${local.eks_cluster_name}"  = "shared"
    "karpenter.sh/discovery/${local.eks_cluster_name}" = "-"
  }
}

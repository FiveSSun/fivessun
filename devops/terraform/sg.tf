resource "aws_security_group" "app_mesh" {
  name        = "app-mesh"
  description = "Connect with other services"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    self      = true
    security_groups = [
      #      aws_security_group.app_ingress.id,
    ]
    cidr_blocks = [
      module.vpc.vpc_cidr_block,
    ]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    "Name"                                             = "app-mesh"
    "karpenter.sh/discovery/${local.eks_cluster_name}" = "-"
  }
}

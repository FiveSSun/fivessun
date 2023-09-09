provider "aws" {
  region = "ap-northeast-2"
  default_tags {
    tags = {
      terraform    = true
      monitor      = false
      account-name = "fivessun"
    }
  }
}

locals {
  eks_cluster_name  = "fivessun-1-27-cdsnl"
  # eks_oidc_url_path = replace(module.eks_fivessun.cluster_oidc_issuer_url, "https://", "")
}

provider "aws" {
  region = "ap-northeast-2"
  default_tags {
    tags = {
      terraform       = true
      monitor         = false
      account-name    = "fivessun"
      hashicorp-learn = "refresh"
    }
  }
}

locals {
  eks_cluster_name = "fivessun-1-27-ioewq"
}

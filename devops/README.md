# Fivessun Devops

Manage AWS Infrastructure with Terraform.

## Setup
To run terraform locally, you will need to set the following environment variables:
```dotenv
TF_VAR_enable_local=true
AWS_PROFILE={{ aws sso profile }}
```


## Before Use Argocd
- argocd
```bash
$ kubectl create namespace argocd
$ kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```
```bash
$ kubectl port-forward svc/argocd-server -n argocd 8080:80
$ kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

- external secrets
```bash
$ helm upgrade --install external-secrets external-secrets/external-secrets \
--version 0.9.4
-n external-secrets \
-f external-secrets.yaml \
--create-namespace
```

- karpenter
```bash
$ helm upgrade --install karpenter oci://public.ecr.aws/karpenter/karpenter --version v0.29.2 -n karpenter -f app/conf/karpenter/default.yaml --create-namespace
```
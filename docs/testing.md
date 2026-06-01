# Testing

## Offline checks

Run `python3 -m unittest discover -s tests -v`, `python3 tools/check_repo.py`, and `bash -n bootstrap/startup.sh`. Python uses the standard library; PKI tests require OpenSSL. Terraform tests use mock Google/random providers, so no GCP credentials or cloud API apply are required. Run `terraform -chdir=terraform init -backend=false`, `terraform -chdir=terraform validate`, then `terraform -chdir=terraform test`.

Mock plans assert private addressing, failure-domain placement, access controls, deletion protection, optional NAT/IAP, input validation and complete node secret references. They cannot verify GCP IAM propagation, API quotas or network reachability.


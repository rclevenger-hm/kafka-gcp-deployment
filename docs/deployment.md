# Deployment

## Prerequisites

Use a dedicated, billing-enabled project, Terraform 1.12.2 or later in the 1.x line, gcloud, Python 3.11+, OpenSSL, and an administrator capable of managing Compute, VPC, DNS, service accounts, project APIs and per-secret IAM. Terraform's deployment identity must have `iam.serviceAccounts.actAs` on the node accounts. Grant deployment permissions only to your reviewed operator/CI principal; do not give broad project roles to the Kafka VMs.

Select three valid zones in one region and confirm quotas for six VMs, six SSDs, internal addresses, Cloud NAT, service accounts, and CPUs. Provide a private client/collector path before testing. Default capacity is 3 x 500 GiB broker SSD plus 3 x 50 GiB controller SSD, six boot disks, compute, NAT, DNS, cross-zone traffic and logging. Review [capacity](capacity-planning.md) before creating resources.


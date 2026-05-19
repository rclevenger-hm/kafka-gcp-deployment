# Deployment

## Prerequisites

Use a dedicated, billing-enabled project, Terraform 1.12.2 or later in the 1.x line, gcloud, Python 3.11+, OpenSSL, and an administrator capable of managing Compute, VPC, DNS, service accounts, project APIs and per-secret IAM. Terraform's deployment identity must have `iam.serviceAccounts.actAs` on the node accounts. Grant deployment permissions only to your reviewed operator/CI principal; do not give broad project roles to the Kafka VMs.

Select three valid zones in one region and confirm quotas for six VMs, six SSDs, internal addresses, Cloud NAT, service accounts, and CPUs. Provide a private client/collector path before testing. Default capacity is 3 x 500 GiB broker SSD plus 3 x 50 GiB controller SSD, six boot disks, compute, NAT, DNS, cross-zone traffic and logging. Review [capacity](capacity-planning.md) before creating resources.

## State and authentication

Authenticate with `gcloud auth application-default login`, or use an approved short-lived workload identity. Create a dedicated GCS state bucket before initialization. Enable uniform bucket-level access, public access prevention and object versioning. Restrict `roles/storage.objectAdmin` to your deployment identities on that bucket. Do not use service-account key JSON files.

Copy `terraform/backend.hcl.example` to `terraform/backend.hcl` and select an existing bucket and unique environment prefix. The GCS backend provides locking; do not disable locking. Protect state access because metadata, addresses and identity references are operationally sensitive even though TLS keys are absent. A workstation using `init -backend=false` for tests must reinitialize with `-reconfigure` before a real deployment.


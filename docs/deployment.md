# Deployment

## Prerequisites

Use a dedicated, billing-enabled project, Terraform 1.12.2 or later in the 1.x line, gcloud, Python 3.11+, OpenSSL, and an administrator capable of managing Compute, VPC, DNS, service accounts, project APIs and per-secret IAM. Terraform's deployment identity must have `iam.serviceAccounts.actAs` on the node accounts. Grant deployment permissions only to your reviewed operator/CI principal; do not give broad project roles to the Kafka VMs.

Select three valid zones in one region and confirm quotas for six VMs, six SSDs, internal addresses, Cloud NAT, service accounts, and CPUs. Provide a private client/collector path before testing. Default capacity is 3 x 500 GiB broker SSD plus 3 x 50 GiB controller SSD, six boot disks, compute, NAT, DNS, cross-zone traffic and logging. Review [capacity](capacity-planning.md) before creating resources.

## State and authentication

Authenticate with `gcloud auth application-default login`, or use an approved short-lived workload identity. Create a dedicated GCS state bucket before initialization. Enable uniform bucket-level access, public access prevention and object versioning. Restrict `roles/storage.objectAdmin` to your deployment identities on that bucket. Do not use service-account key JSON files.

Copy `terraform/backend.hcl.example` to `terraform/backend.hcl` and select an existing bucket and unique environment prefix. The GCS backend provides locking; do not disable locking. Protect state access because metadata, addresses and identity references are operationally sensitive even though TLS keys are absent. A workstation using `init -backend=false` for tests must reinitialize with `-reconfigure` before a real deployment.

## TLS preparation

Each node needs a certificate with its FQDN in DNS SAN and exactly `CN=<node-name>`. Include both serverAuth and clientAuth usage. Keys must be unencrypted PKCS8 PEM. Use an organizational CA and include its trusted CA chain in `ca`; this repository's generator is for lab certificates only.

For a disposable lab:

```bash
python3 tools/lab_pki.py --out pki --prefix kafka --domain kafka.internal --brokers 3
```

The command refuses to overwrite an existing directory, issues 30-day certificates and creates an admin client identity. Keep the CA key offline. Never upload `ca.key`, the admin private key or another node's key to a node secret.

Enable Secret Manager, then create one secret per node and upload only its JSON bundle. For example:

```bash
gcloud services enable secretmanager.googleapis.com --project PROJECT_ID
gcloud secrets create kafka-broker-1-tls --replication-policy=automatic --project PROJECT_ID
gcloud secrets versions add kafka-broker-1-tls --data-file=pki/kafka-broker-1.json --project PROJECT_ID
```

Repeat for all controllers/brokers. A bundle has `certificate`, `private_key`, and `ca` PEM string fields. Put the returned **numeric** version paths into `tls_secret_versions`. Runtime identities receive accessor permission only on their own secret; secret-level IAM permits versions of that secret, while desired configuration pins the selected version. No secret payload is passed to Terraform. Terraform will reject missing node entries or duplicate version references.

## Plan and apply

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
cp terraform/backend.hcl.example terraform/backend.hcl
# Edit both local files for your project, network, secrets and state bucket.
terraform -chdir=terraform init -reconfigure -backend-config=backend.hcl
terraform -chdir=terraform plan -out=deployment.tfplan
terraform -chdir=terraform apply deployment.tfplan
terraform -chdir=terraform output
```

Inspect the saved plan: no public IPs, six default disks/nodes, three distinct zones, narrow client/metrics rules, numeric secret versions, intended region and protected storage. Bootstrap can take several minutes after VM creation; a successful apply is not Kafka readiness. If organization policies prevent external package downloads, supply an approved egress mirror strategy before disabling NAT.


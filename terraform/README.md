# Terraform interface

Read the [deployment guide](../docs/deployment.md) before applying. This root module creates a dedicated VPC and a self-managed Kafka cluster, not Google Managed Service for Apache Kafka.

Inputs and their validation are defined in [variables.tf](variables.tf). Begin with [terraform.tfvars.example](terraform.tfvars.example) and [backend.hcl.example](backend.hcl.example). The GCS state bucket must already exist. Use separate state prefixes/projects for each environment.

Outputs include `bootstrap_servers`, `cluster_id`, `inventory`, and `prometheus_targets`. Every node has a pinned numeric Secret Manager version and its own service account. Secret payloads are fetched on the VM; no secret-version data source is used.

The node module has no provisioner or local-exec hooks. Startup uses instance metadata containing only source code, nonsecret settings, and secret references. Changing metadata does not replace all VMs. Runtime changes require a controlled one-node procedure in the [upgrade runbook](../docs/runbooks/rolling-upgrade.md).

Persistent disks use `prevent_destroy`; API deletion protection guards VMs. Neither protection replaces backups. Review [decommissioning](../docs/runbooks/decommission.md) before removing resources. Machine type changes may require manual stop/start and intentionally do not receive blanket stop permission from Terraform.

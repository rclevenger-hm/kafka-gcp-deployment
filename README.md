# Kafka on Google Cloud

Private, reproducible Apache Kafka on Compute Engine: dedicated KRaft controllers, multi-zone brokers, mutual TLS, persistent disks, and operations tooling.

[![Validation](https://github.com/rclevenger-hm/kafka-gcp-deployment/actions/workflows/ci.yml/badge.svg)](https://github.com/rclevenger-hm/kafka-gcp-deployment/actions/workflows/ci.yml)

**Status:** implemented reference deployment. Offline contracts and a local six-process integration suite are included. A real GCP apply, IAP access, zone-loss drill, production load test, and recovery rehearsal remain acceptance gates. Do not treat CI as evidence of a production deployment.

## Included

- Terraform provisions a private VPC, Cloud NAT, private DNS, reserved internal addresses, six or more Shielded VMs, dedicated SSDs, scoped node identities, and firewall rules.
- Three dedicated Kafka 4.1.2 KRaft controllers span three zones. Three or more rack-aware brokers use replication factor 3 and minimum ISR 2.
- Mutual TLS protects client, replication and controller listeners. ACL authorization defaults closed. Numeric Secret Manager versions keep private keys out of Terraform state and instance metadata.
- Bootstrap verifies artifacts and storage identity, installs a hardened systemd service, and refuses unattended runtime changes.
- Tools cover lab PKI, health gates, unique-topic produce/consume tests, and failure-aware capacity estimates.
- Prometheus exporter configuration, alert rules and rule tests, a Grafana dashboard, and recovery/upgrade/security runbooks are included.

## Start here

1. Read the [architecture](docs/architecture.md) and [cost model](docs/capacity-planning.md).
2. Follow the [deployment guide](docs/deployment.md): create state storage and node TLS secrets before applying Terraform.
3. Pass [acceptance checks](docs/acceptance.md) from a private client host.
4. Connect an existing private monitoring stack using the [observability guide](docs/observability.md).

```bash
python3 -m unittest discover -s tests -v
python3 tools/check_repo.py
terraform -chdir=terraform init -backend=false
terraform -chdir=terraform validate
terraform -chdir=terraform test
```

No command above creates cloud infrastructure. A deploy requires an explicit authenticated Terraform plan/apply and incurs GCP charges. Local broker integration instructions are in [testing](docs/testing.md).

## Documentation

[Documentation index](docs/README.md) · [Terraform interface](terraform/README.md) · [OCI parity](docs/oci-parity.md) · [Roadmap](docs/roadmap.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)

The design builds on the operational goals of [kafka-oci-deployment](https://github.com/rclevenger-hm/kafka-oci-deployment). [LICENSE](LICENSE).

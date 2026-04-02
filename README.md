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


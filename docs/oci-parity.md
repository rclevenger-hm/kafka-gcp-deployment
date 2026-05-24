# OCI reference parity

Reviewed baseline: `rclevenger-hm/kafka-oci-deployment`, main commit `9f2b2b41d36f75a1fe58f040f3f54ddd3d3b02dc`. That snapshot describes an intended private Kafka architecture and includes a Terraform VCN/subnet/client-NSG foundation plus operations, capacity, upgrade and failure-exercise documents. It explicitly labels itself a scaffold.

| Capability | OCI reviewed snapshot | This GCP implementation |
| --- | --- | --- |
| Private network | VCN/subnet/NSG implementation | VPC/subnet/private access, NAT, scoped service-account rules |
| Multi-zone compute | Architecture guidance | Three controllers and three-plus brokers across three zones |
| Durable node storage | Design guidance | Dedicated protected persistent SSD per node and guarded mounts |
| DNS/advertised listeners | Design guidance | Reserved addresses, private DNS and generated broker listeners |
| KRaft bootstrap | Planned | Stable cluster/directory UUIDs and dynamic quorum formatting |
| TLS and secrets | Recommended | Mandatory mTLS, numeric Secret Manager versions, per-node IAM |
| Authorization | Design guidance | Default-deny ACL authorizer and explicit admin principals |
| Service hardening | Planned | Unprivileged systemd runtime and verified artifact installation |
| Validation | Network/docs checks | Python regressions, mock Terraform plans, six-process TLS/ACL integration |
| Observability | Signal/alert guidance | Exporter config, dashboard, alerts and rule tests; collector external |
| Operations | Capacity/failure/upgrade guides | Equivalent guides plus executable health, smoke, PKI and sizing tools |
| Production evidence | Not claimed | Real GCP acceptance gates remain open |

The improvement is implementation depth and testability. It is not a claim of superior measured throughput, cloud availability or production readiness.

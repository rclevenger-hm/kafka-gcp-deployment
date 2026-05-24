# Roadmap

## Implemented

Private multi-zone infrastructure; stable KRaft identity; checksummed bootstrap; protected data mounts; mTLS and ACLs; node-scoped secret access; offline tests and real-process integration harness; monitoring assets; capacity and lifecycle tools; deployment, incident, failure, upgrade, rotation and recovery guides.

## Before production acceptance

- Run and retain real GCP apply/IAP/network/disk/reboot evidence.
- Benchmark workload throughput, disk latency, JVM pressure, partition skew and zone-loss recovery.
- Integrate host metrics, logs, consumer lag, certificate expiry and alert delivery.
- Rehearse controller-disk recovery and cross-region failover with measured RPO/RTO.
- Replace lab PKI with organizational issuance/rotation and review organization policies.

## Follow-on improvements

Immutable image builds; deployment-specific Workload Identity Federation examples; automated rebalance planning with admission/health gates; exporter/host metric coverage expansion; tiered storage evaluation; managed Kafka and GKE/Strimzi alternatives. These are not advertised as existing features.

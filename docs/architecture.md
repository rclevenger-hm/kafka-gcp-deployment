# Architecture

The default deployment has three dedicated KRaft controllers and three brokers across three zones in one GCP region. Controller IDs start at 100; broker IDs start at 1. Terraform retains one cluster UUID and initial controller directory UUIDs. These values are part of the identity of the cluster, not disposable configuration.

```mermaid
flowchart TD
  Clients["Private clients"] --> DNS["Private Cloud DNS"]
  DNS --> Brokers["Brokers across three zones"]
  Brokers --> Quorum["Three dedicated controllers"]
  Brokers --> Data["Per-node persistent SSDs"]
  Quorum --> Metadata["Persistent metadata SSDs"]
  Secrets["Per-node TLS secrets"] --> Brokers
  Secrets --> Quorum
  IAP["IAP and OS Login"] --> Brokers
  Brokers --> Metrics["Private Prometheus collector"]
```


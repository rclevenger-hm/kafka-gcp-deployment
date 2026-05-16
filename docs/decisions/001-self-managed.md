# Decision 001: self-managed Compute Engine

Use Compute Engine to match the operational intent of the OCI reference: direct control over Kafka topology, disks, security and lifecycle. This costs more operator time than a managed service. Teams that primarily need Kafka APIs should evaluate Google Managed Service for Apache Kafka before accepting self-management responsibilities.

Dedicated controllers allow independent maintenance and avoid combining metadata quorum with broker workload pressure. Three zones provide a single-zone failure model; this is not regional DR. Kubernetes/Strimzi and managed Kafka are future alternatives, not hidden deployment modes in the current root module.

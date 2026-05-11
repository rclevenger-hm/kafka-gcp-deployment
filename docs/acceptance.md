# Deployment acceptance

CI validates source contracts and real local Kafka behavior. Production acceptance requires environment-specific evidence. Record commit SHA, Terraform state version, project, region, zones, Kafka version, certificate expiration, test timestamp, operator and rollback owner.

## Required evidence

- A reviewed real Terraform plan and successful apply; all VMs use internal addresses only.
- Every VM boots with its correct data disk and survives reboot without formatting or changing cluster identity.
- IAP/OS Login works for approved administrators and fails for an unapproved identity.
- Kafka quorum shows all three expected voters, a leader, zero lag, and no offline/under-replicated/under-min-ISR partitions.
- The smoke tool creates a unique RF3/minISR2 topic, roundtrips exact data and deletes only that topic.
- A trusted but unauthorized client certificate is denied. An untrusted client and wrong hostname also fail.
- Prometheus discovers all nodes, dashboard metrics have expected labels and a test alert reaches the on-call channel.
- Disk/host/log/certificate/consumer-lag monitoring is installed and thresholds are tied to response time.
- A broker loss and a controller loss recover under representative traffic; a zone-loss drill meets the stated objective.
- A rolling restart and certificate rotation preserve data and client availability.
- Recovery to a separate cluster is rehearsed with measured RPO/RTO and consumer-offset handling.

Use [failure exercises](failure-exercises.md) and [testing](testing.md). Do not mark a gate complete merely because a document or test script exists.

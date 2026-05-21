# Failure exercises

Run destructive drills only in an explicitly approved environment with a named incident lead, a recovery plan and a client traffic baseline. Start with staging. Capture cluster ID, broker IDs, controller membership, topic assignments, lag, throughput and client p99 before each drill. Change one failure domain at a time.

| Exercise | Method | Pass criterion | Abort signal |
| --- | --- | --- | --- |
| Broker process loss | Stop one Kafka service | Writes continue where ISR permits; restart restores ISR | Any offline partition or unexpected second loss |
| Controller loss | Stop one controller | Remaining majority elects/stays healthy | Loss of quorum or second controller unhealthy |
| VM reboot | Reboot one node | Existing disk identity retained; no format | Wrong disk, missing identity or TLS error |
| Zone disruption | Approved network/VM isolation of one zone | Measured client and recovery objectives met | Data safety assumptions violated |
| Disk pressure | Dedicated disposable test disk/workload | Alert fires with response headroom | Production disk affected or unbounded writes |
| Certificate rotation | Rotate one pinned version | No unauthorized access and clients recover | Trust chain/hostname/principal mismatch |
| DNS failure | Controlled test-client resolver failure | Clear alert/diagnosis; recovery on DNS restore | Cluster-wide unintended resolver impact |

After each drill, require healthy quorum, no unavailable/under-min-ISR/under-replicated partitions, a passing smoke test and restored monitoring. Record the observed recovery time and compare it with [capacity](capacity-planning.md). Do not force unclean leader election to make a drill appear successful.

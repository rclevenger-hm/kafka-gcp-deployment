# Rolling runtime changes

Test the target Kafka/JDK/configuration in staging and read Apache's version-specific upgrade notes. Change the pinned artifact version and digest together. The current renderer targets Kafka 4.1.x. Feature-level upgrades and controller membership changes are separate operations; do not finalize a feature level until the rollback window closes.

1. Confirm `tools/health.py` and `tools/smoke.py` pass, and no replica reassignment or other maintenance is active. Record source/target versions, cluster identity and rollback commands.
2. Apply the reviewed metadata-only Terraform change. Check the plan does not replace disks or multiple VMs. Metadata changes alone do not roll services.
3. On one node, run `sudo google_metadata_script_runner startup` to stage the current files. For changed configuration it intentionally stops with a pending-change message before touching the service.
4. With health gates still satisfied, run `sudo python3 /opt/kafka-bootstrap/provision.py --config /opt/kafka-bootstrap/config.json --apply-change` on that one node. Follow logs, service state and metrics.
5. Wait for healthy quorum, recovered ISR and a successful smoke test before touching another node. Follow Apache's controller/broker ordering guidance for the specific upgrade; never restart a quorum majority together.
6. Stop immediately on new offline partitions, increasing quorum lag, persistent replication loss or client SLO breach. Revert desired metadata and use the same one-node procedure only if the release supports downgrade and no incompatible metadata feature has been enabled.

Startup verifies downloads before stopping Kafka, but installation success is only process-level readiness. External health gates are mandatory. Existing binary versions are retained under `/opt/kafka_2.13-VERSION`; old TLS secret versions must remain available until rollback is closed. Automated fleet-wide restarts are deliberately not provided.

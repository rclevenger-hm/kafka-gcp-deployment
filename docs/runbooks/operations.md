# Incident response

Start with client impact and data durability. Preserve the cluster ID, controller membership, topic ISR, recent deployment changes and relevant logs. Check private DNS and TCP reachability, then TLS chain/expiry, Kafka ACL failures, disk pressure and service status. Use `journalctl -u kafka` and startup logs on the affected VM.

Run `tools/health.py` from a private authenticated admin host. If partitions are offline, restore original replicas and storage before considering data-loss actions. If under-min-ISR is nonzero, acknowledge that writes may be intentionally rejected to preserve durability; do not lower minISR as an automatic fix. If controller quorum is unavailable, recover original metadata disks and a majority of members. Do not reformat controllers or generate a new cluster UUID.

For growing consumer lag, compare ingress, processing rate, rebalance churn, downstream latency and partition skew. Adding brokers alone does not accelerate a slow downstream dependency. For disk pressure, measure growth and retention before expanding storage; do not delete segment files manually.

After recovery, require healthy quorum/ISR, a passing unique-topic roundtrip, stable client latency and monitored recovery bandwidth. Record the trigger, contributing changes, duration, evidence and concrete prevention work.

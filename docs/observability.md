# Observability

The checksummed JMX exporter starts inside each Kafka JVM on TCP 9404. Kafka listeners remain mutually authenticated; the metrics endpoint must be reachable only from trusted collectors. The Terraform metrics CIDR list defaults empty. No unauthenticated remote JMX/RMI port is opened.

## Connect a collector

Export targets with `terraform -chdir=terraform output -json prometheus_targets > kafka-targets.json`. Install that file in your existing private Prometheus file-discovery path. Use [the scrape example](../monitoring/prometheus.yml.example), [alerts](../monitoring/alerts.yml), and [Grafana dashboard](../monitoring/grafana-dashboard.json). Set the dashboard's Prometheus datasource on import. Prometheus/Alertmanager/Grafana servers are not provisioned here.

## Actionable signals

| Signal | Default action | First response |
| --- | --- | --- |
| Offline partitions | Page after 1 minute | Check broker reachability and disk |
| Under minimum ISR | Page after 1 minute | Protect durability, restore replicas |
| Under-replicated partitions | Ticket after 5 minutes | Measure recovery and saturation |
| Exporter unavailable | Page after 2 minutes | Distinguish process failure from scrape path |
| Active controller count != 1 | Page after 2 minutes | Inspect quorum and controller logs |
| All target telemetry absent | Page after 5 minutes | Restore discovery/collector path |

These are starting thresholds. Change them with SLO and recovery evidence. Planned maintenance silences must expire automatically. Alert rules include behavioral tests using Prometheus `promtool`.

## Additional production instrumentation

Install your approved host monitoring/logging collector for disk usage/latency, memory, CPU, kernel errors and systemd logs. Monitor certificate expiration and Secret Manager audit logs. Consumer lag is workload-specific and requires consumer/client instrumentation or a separately authenticated lag exporter. It is not inferred from broker throughput. Export logs with redaction and retention rules; disk growth forecasting and application produce/fetch SLOs are acceptance gates.

# Observability

The checksummed JMX exporter starts inside each Kafka JVM on TCP 9404. Kafka listeners remain mutually authenticated; the metrics endpoint must be reachable only from trusted collectors. The Terraform metrics CIDR list defaults empty. No unauthenticated remote JMX/RMI port is opened.

## Connect a collector

Export targets with `terraform -chdir=terraform output -json prometheus_targets > kafka-targets.json`. Install that file in your existing private Prometheus file-discovery path. Use [the scrape example](../monitoring/prometheus.yml.example), [alerts](../monitoring/alerts.yml), and [Grafana dashboard](../monitoring/grafana-dashboard.json). Set the dashboard's Prometheus datasource on import. Prometheus/Alertmanager/Grafana servers are not provisioned here.


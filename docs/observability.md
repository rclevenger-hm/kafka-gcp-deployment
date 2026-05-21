# Observability

The checksummed JMX exporter starts inside each Kafka JVM on TCP 9404. Kafka listeners remain mutually authenticated; the metrics endpoint must be reachable only from trusted collectors. The Terraform metrics CIDR list defaults empty. No unauthenticated remote JMX/RMI port is opened.


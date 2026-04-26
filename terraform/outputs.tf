output "bootstrap_servers" {
  description = "Private TLS bootstrap endpoints; clients must reach all advertised broker names."
  value       = join(",", [for name in sort(keys(local.brokers)) : "${name}.${var.dns_domain}:9092"])
}

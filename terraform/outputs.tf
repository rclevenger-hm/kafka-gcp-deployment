output "bootstrap_servers" {
  description = "Private TLS bootstrap endpoints; clients must reach all advertised broker names."
  value       = join(",", [for name in sort(keys(local.brokers)) : "${name}.${var.dns_domain}:9092"])
}
output "cluster_id" {
  description = "Stable KRaft cluster identity; retain with disaster recovery evidence."
  value       = random_id.cluster.b64_url
}
output "inventory" {
  description = "Node identity, address and zone for operations; no secret payloads."
  value = { for name, n in local.nodes : name => {
    role           = n.role, node_id = n.id, zone = n.zone,
    fqdn           = "${name}.${var.dns_domain}", ip = google_compute_address.node[name].address,
    secret_version = lookup(var.tls_secret_versions, name, "MISSING")
  } }
}
output "prometheus_targets" {
  description = "File service discovery entries for a private Prometheus collector."
  value = [for name, n in local.nodes : {
    targets = ["${name}.${var.dns_domain}:9404"]
    labels  = { cluster = var.name_prefix, role = n.role, zone = n.zone }
  }]
}

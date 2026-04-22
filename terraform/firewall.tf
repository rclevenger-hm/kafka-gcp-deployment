resource "google_compute_firewall" "controller" {
  name                    = "${var.name_prefix}-controller"
  network                 = google_compute_network.kafka.name
  source_service_accounts = [for n in google_service_account.node : n.email]
  target_service_accounts = [for name in keys(local.controllers) : google_service_account.node[name].email]
  allow {
    protocol = "tcp"
    ports    = ["9093"]
  }
}
resource "google_compute_firewall" "replication" {
  name                    = "${var.name_prefix}-replication"
  network                 = google_compute_network.kafka.name
  source_service_accounts = [for n in google_service_account.node : n.email]
  target_service_accounts = [for name in keys(local.brokers) : google_service_account.node[name].email]
  allow {
    protocol = "tcp"
    ports    = ["9094"]
  }
}

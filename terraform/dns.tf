resource "google_dns_managed_zone" "kafka" {
  name       = "${var.name_prefix}-private"
  dns_name   = "${var.dns_domain}."
  visibility = "private"
  private_visibility_config {
    networks { network_url = google_compute_network.kafka.id }
  }
  depends_on = [google_project_service.api]
}

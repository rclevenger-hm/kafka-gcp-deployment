resource "google_dns_managed_zone" "kafka" {
  name       = "${var.name_prefix}-private"
  dns_name   = "${var.dns_domain}."
  visibility = "private"
  private_visibility_config {
    networks { network_url = google_compute_network.kafka.id }
  }
  depends_on = [google_project_service.api]
}
resource "google_compute_address" "node" {
  for_each     = local.nodes
  name         = "${each.key}-ip"
  address_type = "INTERNAL"
  region       = var.region
  subnetwork   = google_compute_subnetwork.kafka.id
  address      = cidrhost(var.subnet_cidr, each.value.host)
}

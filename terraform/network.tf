resource "google_compute_network" "kafka" {
  name                    = "${var.name_prefix}-vpc"
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
  depends_on              = [google_project_service.api]
}
resource "google_compute_subnetwork" "kafka" {
  name                     = "${var.name_prefix}-private"
  region                   = var.region
  ip_cidr_range            = var.subnet_cidr
  network                  = google_compute_network.kafka.id
  private_ip_google_access = true
  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.1
    metadata             = "INCLUDE_ALL_METADATA"
  }
}
resource "google_compute_router" "egress" {
  count   = var.enable_nat ? 1 : 0
  name    = "${var.name_prefix}-router"
  region  = var.region
  network = google_compute_network.kafka.id
}
resource "google_compute_router_nat" "egress" {
  count                              = var.enable_nat ? 1 : 0
  name                               = "${var.name_prefix}-nat"
  router                             = google_compute_router.egress[0].name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"
  subnetwork {
    name                    = google_compute_subnetwork.kafka.id
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }
  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

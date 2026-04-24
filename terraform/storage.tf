resource "google_compute_disk" "data" {
  for_each = local.nodes
  name     = "${each.key}-data"
  zone     = each.value.zone
  type     = "pd-ssd"
  size     = each.value.role == "broker" ? var.broker_disk_gb : var.controller_disk_gb
  labels   = merge(local.labels, { role = each.value.role })
  lifecycle { prevent_destroy = true }
  depends_on = [google_project_service.api]
}

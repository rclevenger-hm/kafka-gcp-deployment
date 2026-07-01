resource "google_project_service" "api" {
  for_each           = toset(["iam.googleapis.com", "compute.googleapis.com", "dns.googleapis.com", "secretmanager.googleapis.com", "logging.googleapis.com", "monitoring.googleapis.com", "iap.googleapis.com"])
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

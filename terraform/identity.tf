resource "google_service_account" "node" {
  for_each     = local.nodes
  account_id   = each.key
  display_name = "Kafka ${each.value.role} ${each.value.id}"
  depends_on   = [google_project_service.api]
}
resource "google_secret_manager_secret_iam_member" "tls" {
  for_each  = local.nodes
  project   = try(split("/", var.tls_secret_versions[each.key])[1], var.project_id)
  secret_id = try(split("/", var.tls_secret_versions[each.key])[3], "missing-secret")
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.node[each.key].email}"
}

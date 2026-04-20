resource "google_service_account" "node" {
  for_each     = local.nodes
  account_id   = each.key
  display_name = "Kafka ${each.value.role} ${each.value.id}"
  depends_on   = [google_project_service.api]
}

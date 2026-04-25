resource "google_compute_instance" "node" {
  for_each                  = local.nodes
  name                      = each.key
  zone                      = each.value.zone
  machine_type              = each.value.role == "broker" ? var.broker_machine_type : var.controller_machine_type
  deletion_protection       = var.deletion_protection
  allow_stopping_for_update = false
  labels                    = merge(local.labels, { role = each.value.role })
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size  = 20
      type  = "pd-balanced"
    }
  }
  attached_disk {
    source      = google_compute_disk.data[each.key].id
    device_name = "kafka-data"
    mode        = "READ_WRITE"
  }
  network_interface {
    subnetwork = google_compute_subnetwork.kafka.id
    network_ip = google_compute_address.node[each.key].address
  }
  service_account {
    email  = google_service_account.node[each.key].email
    scopes = ["cloud-platform"]
  }
  shielded_instance_config {
    enable_secure_boot          = true
    enable_vtpm                 = true
    enable_integrity_monitoring = true
  }
  scheduling {
    preemptible         = false
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
  }
  metadata = {
    enable-oslogin         = "TRUE"
    block-project-ssh-keys = "TRUE"
    serial-port-enable     = "FALSE"
    startup-script         = file("${path.module}/../bootstrap/startup.sh")
    kafka-runtime          = base64gzip(jsonencode(local.runtime_files))
    kafka-config = jsonencode({
      node_id             = each.value.id
      node_name           = each.key
      role                = each.value.role
      zone                = each.value.zone
      fqdn                = "${each.key}.${var.dns_domain}"
      quorum              = local.quorum
      initial_controllers = local.initial_controllers
      cluster_id          = random_id.cluster.b64_url
      super_users         = local.super_users
      tls_secret_version  = lookup(var.tls_secret_versions, each.key, "MISSING")
      kafka_version       = var.kafka_version
      kafka_sha512        = var.kafka_sha512
      retention_hours     = var.retention_hours
    })
  }
  lifecycle {
    precondition {
      condition     = length(setsubtract(toset(keys(local.nodes)), toset(keys(var.tls_secret_versions)))) == 0
      error_message = "tls_secret_versions must contain one existing version for every controller and broker name."
    }
    precondition {
      condition     = length(distinct(values(var.tls_secret_versions))) == length(var.tls_secret_versions)
      error_message = "Each node must have its own TLS secret."
    }
  }
  depends_on = [google_compute_router_nat.egress, google_secret_manager_secret_iam_member.tls, google_dns_record_set.node]
}

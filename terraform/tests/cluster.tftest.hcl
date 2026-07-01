mock_provider "google" {}
mock_provider "random" {
  mock_resource "random_id" {
    defaults = { b64_url = "AAAAAAAAAAAAAAAAAAAAAA" }
  }
}
variables {
  project_id = "kafka-test-project"
  tls_secret_versions = {
    kafka-controller-1 = "projects/kafka-test-project/secrets/kafka-controller-1/versions/1"
    kafka-controller-2 = "projects/kafka-test-project/secrets/kafka-controller-2/versions/1"
    kafka-controller-3 = "projects/kafka-test-project/secrets/kafka-controller-3/versions/1"
    kafka-broker-1     = "projects/kafka-test-project/secrets/kafka-broker-1/versions/1"
    kafka-broker-2     = "projects/kafka-test-project/secrets/kafka-broker-2/versions/1"
    kafka-broker-3     = "projects/kafka-test-project/secrets/kafka-broker-3/versions/1"
  }
}

run "private_topology" {
  command = plan

  assert {
    condition     = contains(keys(google_project_service.api), "iam.googleapis.com")
    error_message = "Node account creation requires the IAM API."
  }

  assert {
    condition     = length(google_compute_instance.node) == 6 && length(google_compute_disk.data) == 6
    error_message = "Default topology needs six independent nodes and disks."
  }
  assert {
    condition     = alltrue([for n in google_compute_instance.node : length(n.network_interface[0].access_config) == 0])
    error_message = "Kafka VMs must not have public addresses."
  }
  assert {
    condition     = alltrue([for n in google_compute_instance.node : n.deletion_protection && n.shielded_instance_config[0].enable_secure_boot])
    error_message = "VM deletion and integrity protections must remain enabled."
  }
  assert {
    condition     = length(google_compute_firewall.clients) == 0 && length(google_compute_firewall.metrics) == 0
    error_message = "Client and metrics ingress must default closed."
  }
  assert {
    condition     = length(toset([for n in values(local.controllers) : n.zone])) == 3
    error_message = "Controllers must span three distinct zones."
  }
  assert {
    condition     = alltrue([for n in google_compute_instance.node : n.metadata["enable-oslogin"] == "TRUE" && n.metadata["block-project-ssh-keys"] == "TRUE"])
    error_message = "Human access must use OS Login."
  }
}

run "client_allowlist" {
  command = plan

  variables { client_cidrs = ["10.60.0.0/24"] }
  assert {
    condition     = google_compute_firewall.clients[0].source_ranges == toset(["10.60.0.0/24"]) && one(google_compute_firewall.clients[0].allow).ports == tolist(["9092"])
    error_message = "Clients must be limited to the client listener."
  }
}

run "nat_opt_out" {
  command = plan

  variables { enable_nat = false }
  assert {
    condition     = length(google_compute_router_nat.egress) == 0
    error_message = "NAT opt-out must avoid creating an egress service."
  }
}

run "iap_opt_out" {
  command = plan

  variables { enable_iap_ssh = false }
  assert {
    condition     = length(google_compute_firewall.iap) == 0
    error_message = "IAP opt-out must not allow SSH."
  }
}

run "reject_public_clients" {
  command = plan
  variables { client_cidrs = ["0.0.0.0/0"] }
  expect_failures = [var.client_cidrs]
}

run "reject_public_metrics" {
  command = plan
  variables { metrics_cidrs = ["0.0.0.0/0"] }
  expect_failures = [var.metrics_cidrs]
}

run "reject_broad_private_network" {
  command = plan
  variables { client_cidrs = ["192.168.0.0/8"] }
  expect_failures = [var.client_cidrs]
}

run "reject_public_subnet" {
  command = plan
  variables { subnet_cidr = "8.8.0.0/16" }
  expect_failures = [var.subnet_cidr]
}

run "reject_tiny_subnet" {
  command = plan
  variables { subnet_cidr = "10.42.1.0/28" }
  expect_failures = [var.subnet_cidr]
}

run "reject_ipv6_subnet" {
  command = plan
  variables { subnet_cidr = "fd00::/64" }
  expect_failures = [var.subnet_cidr]
}

run "reject_fractional_brokers" {
  command = plan
  variables { broker_count = 3.5 }
  expect_failures = [var.broker_count]
}

run "reject_too_few_brokers" {
  command = plan
  variables { broker_count = 2 }
  expect_failures = [var.broker_count]
}

run "reject_duplicate_zones" {
  command = plan
  variables { zones = ["us-central1-a", "us-central1-a", "us-central1-b"] }
  expect_failures = [var.zones]
}

run "reject_wrong_region" {
  command = plan
  variables { zones = ["us-east1-a", "us-east1-b", "us-east1-c"] }
  expect_failures = [var.zones]
}

run "reject_mutable_secret" {
  command = plan
  variables { tls_secret_versions = { kafka = "projects/kafka-test-project/secrets/tls/versions/latest" } }
  expect_failures = [var.tls_secret_versions]
}

run "missing_node_secrets" {
  command = plan
  variables { tls_secret_versions = {} }
  expect_failures = [google_compute_instance.node]
}

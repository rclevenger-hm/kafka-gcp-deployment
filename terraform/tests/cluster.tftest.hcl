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


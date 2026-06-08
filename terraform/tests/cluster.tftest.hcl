mock_provider "google" {}
mock_provider "random" {
  mock_resource "random_id" {
    defaults = { b64_url = "AAAAAAAAAAAAAAAAAAAAAA" }
  }
}

terraform {
  required_version = ">= 1.12.2, < 2.0.0"
  # Keep version attributes on separate lines so Dependabot can update them.
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.46.1"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.7.2"
    }
  }
  backend "gcs" {}
}
provider "google" {
  project = var.project_id
  region  = var.region
}

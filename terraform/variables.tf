variable "project_id" {
  description = "Existing billing-enabled GCP project."
  type        = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id))
    error_message = "Use a valid GCP project ID."
  }
}

variable "region" {
  description = "Region containing all Kafka zones."
  type        = string
  default     = "us-central1"
  validation {
    condition     = can(regex("^[a-z]+-[a-z]+[0-9]+$", var.region))
    error_message = "Use a GCP region such as us-central1."
  }
}

variable "zones" {
  description = "Three distinct zones in the selected region."
  type        = list(string)
  default     = ["us-central1-a", "us-central1-b", "us-central1-c"]
  validation {
    condition     = length(var.zones) == 3 && length(toset(var.zones)) == 3 && alltrue([for z in var.zones : startswith(z, "${var.region}-")])
    error_message = "Select three unique zones in region."
  }
}


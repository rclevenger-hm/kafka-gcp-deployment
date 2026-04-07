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

variable "name_prefix" {
  description = "Resource prefix; keep stable after deployment."
  type        = string
  default     = "kafka"
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,14}[a-z0-9]$", var.name_prefix))
    error_message = "Use 3-16 lowercase letters, digits or hyphens."
  }
}

variable "subnet_cidr" {
  description = "Private RFC1918 IPv4 node subnet, /16 through /24."
  type        = string
  default     = "10.42.10.0/24"
  validation {
    condition     = can(cidrnetmask(var.subnet_cidr)) && can(regex("^(10\\.|192\\.168\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.)", var.subnet_cidr)) && try(tonumber(split("/", var.subnet_cidr)[1]) >= 16 && tonumber(split("/", var.subnet_cidr)[1]) <= 24, false)
    error_message = "Use a private IPv4 subnet between /16 and /24."
  }
}


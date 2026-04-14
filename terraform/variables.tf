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

variable "client_cidrs" {
  description = "Explicit IPv4 client network allowlist; closed by default."
  type        = set(string)
  default     = []
  validation {
    condition     = alltrue([for c in var.client_cidrs : can(cidrnetmask(c)) && try(tonumber(split("/", c)[1]) >= 8, false) && can(regex("^(10\\.|192\\.168\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.)", c)) && try(tonumber(split("/", c)[1]) >= (startswith(c, "10.") ? 8 : startswith(c, "172.") ? 12 : 16), false)])
    error_message = "Clients must use narrowly scoped RFC1918 IPv4 CIDRs."
  }
}

variable "metrics_cidrs" {
  description = "Private collector networks allowed to scrape port 9404."
  type        = set(string)
  default     = []
  validation {
    condition     = alltrue([for c in var.metrics_cidrs : can(cidrnetmask(c)) && try(tonumber(split("/", c)[1]) >= 16, false) && can(regex("^(10\\.|192\\.168\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.)", c))])
    error_message = "Metrics require private IPv4 CIDRs of /16 or narrower."
  }
}

variable "broker_count" {
  description = "Broker count; adding brokers does not reassign partitions."
  type        = number
  default     = 3
  validation {
    condition     = var.broker_count >= 3 && var.broker_count <= 18 && floor(var.broker_count) == var.broker_count
    error_message = "Use an integer broker count from 3 to 18."
  }
}

variable "broker_machine_type" {
  description = "Broker machine type; load test disk and network performance."
  type        = string
  default     = "e2-standard-4"
}

variable "controller_machine_type" {
  description = "Dedicated controller machine type."
  type        = string
  default     = "e2-standard-2"
}

variable "broker_disk_gb" {
  description = "Per-broker persistent SSD capacity."
  type        = number
  default     = 500
  validation {
    condition     = var.broker_disk_gb >= 100 && floor(var.broker_disk_gb) == var.broker_disk_gb
    error_message = "Use at least 100 GiB."
  }
}

variable "controller_disk_gb" {
  description = "Controller metadata disk capacity."
  type        = number
  default     = 50
  validation {
    condition     = var.controller_disk_gb >= 20 && floor(var.controller_disk_gb) == var.controller_disk_gb
    error_message = "Use at least 20 GiB."
  }
}

variable "dns_domain" {
  description = "Private DNS suffix without trailing dot; dedicated zone."
  type        = string
  default     = "kafka.internal"
  validation {
    condition     = can(regex("^[a-z][a-z0-9.-]*[a-z0-9]$", var.dns_domain)) && strcontains(var.dns_domain, ".")
    error_message = "Use a lowercase DNS domain with no trailing dot."
  }
}

variable "tls_secret_versions" {
  description = "Node name -> existing Secret Manager numeric version path; payload never enters state."
  type        = map(string)
  validation {
    condition     = alltrue([for s in values(var.tls_secret_versions) : can(regex("^projects/[a-z0-9-]+/secrets/[A-Za-z0-9_-]+/versions/[1-9][0-9]*$", s))])
    error_message = "Pin numeric Secret Manager versions; latest is prohibited."
  }
}

variable "admin_principals" {
  description = "Kafka certificate principals allowed to administer the cluster."
  type        = set(string)
  default     = ["User:CN=kafka-admin"]
  validation {
    condition     = length(var.admin_principals) > 0 && alltrue([for p in var.admin_principals : can(regex("^User:CN=[a-zA-Z0-9._-]+$", p))])
    error_message = "Use explicit simple certificate CN principals."
  }
}

variable "deletion_protection" {
  description = "Compute API deletion protection; disks additionally have prevent_destroy."
  type        = bool
  default     = true
}

variable "enable_iap_ssh" {
  description = "Allow SSH only from Google IAP; IAM still required."
  type        = bool
  default     = true
}

variable "enable_nat" {
  description = "Cloud NAT for apt and pinned artifact downloads. Disable only with an egress alternative."
  type        = bool
  default     = true
}


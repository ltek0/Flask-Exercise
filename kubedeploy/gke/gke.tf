variable "project_id" {
  type    = string
  default = "cloud-web-app-dev"
}

variable "cluster_name" {
  type    = string
  default = "ea-cluster"
}

variable "vpc_name" {
  type    = string
  default = "ea-Project"
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.123.0.0/16"
}

variable "vpc_azs" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b"]
}

variable "subnets" {
  type = map(list(string))
  default = {
    "public_subnets"  = ["10.123.1.0/24", "10.123.2.0/24"],
    "private_subnets" = ["10.123.3.0/24", "10.123.4.0/24"],
    "intra_subnets"   = ["10.123.5.0/24", "10.123.6.0/24"]
  }
}

resource "google_compute_network" "main" {
  name                            = "main"
  routing_mode                    = "REGIONAL"
  auto_create_subnetworks         = false
  mtu                             = 1460
  delete_default_routes_on_create = false

  depends_on = [
    google_project_service.compute,
    google_project_service.container
  ]
}

resource "google_compute_subnetwork" "public-subnetwork" {
  name          = "terraform-public-subnetwork"
  ip_cidr_range = "10.2.0.0/16"
  region        = var.region
  network       = google_compute_network.main.name
}

resource "google_compute_subnetwork" "private-subnetwork" {
  name                     = "terraform-private-subnetwork"
  ip_cidr_range            = "10.3.0.0/16"
  region                   = var.region
  network                  = google_compute_network.main.name
  private_ip_google_access = true
}

resource "google_compute_router" "router" {
  name    = "nat-router"
  network = "main"
  region  = var.region
  
  depends_on = [google_compute_network.main]
}

resource "google_compute_router_nat" "nat" {
  name                               = "my-router-nat"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
  depends_on = [google_compute_network.main]
} 

resource "google_project_service" "compute" {
  service                    = "compute.googleapis.com"
  disable_dependent_services = true
}

resource "google_project_service" "container" {
  service                    = "container.googleapis.com"
  disable_dependent_services = true
}

resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.region

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.private-subnetwork.name

}

resource "google_container_node_pool" "primary_preemptible_nodes" {
  name       = "ea-proj-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = 1

  node_config {
    preemptible  = true
    machine_type = "e2-medium"

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }
}
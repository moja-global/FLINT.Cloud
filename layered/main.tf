# Modifiable variables
variable "project" {
  type = string
  default = "flint-cloud"
}

variable "region" {
  type = string
  default = "us-central1"
}

variable "zone" {
  type = string
  default = "us-central1-a"
}

variable "ingress_name" {
  type = string
  default = "fc-ingress"
}

variable "cr_processor_name" {
  type = string
  default = "fc-cr-processor"
}

variable "gce_processor_name" {
  type = string
  default = "fc-gce-processor"
}

variable "gce_processor_cpu" {
  type = number
  default = 4
}

variable "gce_processor_memory" {
  type = number
  default = 10240
}

variable "gce_processor_disk" {
  type = number
  default = 15
}

# Project config
provider "google" {
  credentials = file("service_account.json")
  project = var.project
  region = var.region
}

# Enable APIs
resource "google_project_service" "run" {
  service = "run.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "pubsub" {
  service = "pubsub.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "storage" {
  service = "storage-component.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "compute" {
  service = "compute.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "iam" {
  service = "iam.googleapis.com"
  disable_on_destroy = false
}

# Pub/Sub Topics
resource "google_pubsub_topic" "small-simulations" {
  name = "small-simulations"

  depends_on = [google_project_service.pubsub]
}

resource "google_pubsub_topic" "large-simulations" {
  name = "large-simulations"

  depends_on = [google_project_service.pubsub]
}

# Ingress service
resource "google_cloud_run_service" "fc-ingress" {
  name = var.ingress_name
  location = var.region
  
  template {
    spec {
      containers {
        image = "gcr.io/flint-cloud/ingress:latest"
        env {
          name = "PROJECT_NAME"
          value = var.project
        }
        env {
          name = "GCE_ZONE"
          value = var.zone
        }
        env {
          name = "GCE_NAME"
          value = var.gce_processor_name
        }
      }
    }
  }

  traffic {
    percent = 100
    latest_revision = true
  }
  autogenerate_revision_name = true
  depends_on = [google_project_service.run]
}

output "ingress-url" {
  value = "${google_cloud_run_service.fc-ingress.status[0].url}"
}

data "google_iam_policy" "noauth-ingress" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

resource "google_cloud_run_service_iam_policy" "noauth-ingress" {
  location    = var.region
  project     = var.project
  service     = google_cloud_run_service.fc-ingress.name
  policy_data = data.google_iam_policy.noauth-ingress.policy_data
}

# Cloud Run processor
resource "google_cloud_run_service" "fc-cr-processor" {
  name = var.cr_processor_name
  location = var.region
  
  template {
    spec {
      containers {
        image = "gcr.io/flint-cloud/cr-processor:latest"
        resources {
          limits = {
            cpu    = "4000m"
            memory = "2Gi"
          }
        }
        env {
          name = "LD_LIBRARY_PATH"
          value = "/opt/gcbm:/usr/local//lib:/usr/local//lib/x86_64-linux-gnu:/usr/local/lib:/usr/local/lib/x86_64-linux-gnu:/usr/local/lib:"
        }
        env {
          name = "PROJECT_NAME"
          value = var.project
        }
      }
      timeout_seconds = 3599
    }
  }

  traffic {
    percent = 100
    latest_revision = true
  }
  autogenerate_revision_name = true
  depends_on = [google_project_service.run]
}

data "google_iam_policy" "noauth-cr-processor" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

resource "google_cloud_run_service_iam_policy" "noauth-cr-processor" {
  location    = var.region
  project     = var.project
  service     = google_cloud_run_service.fc-cr-processor.name
  policy_data = data.google_iam_policy.noauth-cr-processor.policy_data
}

resource "google_pubsub_subscription" "small-simulations-sub" {
  name  = "small-simulations-sub"
  topic = google_pubsub_topic.small-simulations.name
  ack_deadline_seconds = 10

  push_config {
    push_endpoint = "${google_cloud_run_service.fc-cr-processor.status[0].url}"
  }

  depends_on = [google_pubsub_topic.small-simulations, google_cloud_run_service.fc-cr-processor]
}

# GCS bucket
resource "google_storage_bucket" "simulation_data_flint-cloud" {
  name = "simulation_data_flint-cloud"
  location = var.region
  force_destroy = true

  depends_on = [google_project_service.storage]
}

# Compute Engine processor
resource "google_pubsub_subscription" "large-simulations-sub" {
  name  = "large-simulations-sub"
  topic = google_pubsub_topic.large-simulations.name
  ack_deadline_seconds = 10

  depends_on = [google_pubsub_topic.large-simulations]
}

module "gce-container" {
  source = "terraform-google-modules/container-vm/google"
  version = "~> 2.0"

  container = {
    image = "gcr.io/flint-cloud/gce-processor:latest"
    securityContext = {
      privileged : true
    }
    env = [
      {
        name = "PROJECT_NAME"
        value = var.project
      },
      {
        name = "GCE_ZONE"
        value = var.zone
      },
      {
        name = "GCE_NAME"
        value = var.gce_processor_name
      }
    ]
  }

  restart_policy = "OnFailure"
}

resource "google_service_account" "gce-sa" {
  account_id   = "fc-gce-processor-service"
  display_name = "FLINT Cloud GCE Service Account"
  project = var.project

  depends_on = [google_project_service.iam]
}

resource "google_project_iam_member" "gce-sa-binding" {
  project = var.project
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.gce-sa.email}"

  depends_on = [google_service_account.gce-sa]
}

resource "google_compute_instance" "fc-gce-processor" {
  name = var.gce_processor_name
  project = var.project
  machine_type = "custom-${var.gce_processor_cpu}-${var.gce_processor_memory}"
  zone = var.zone

  boot_disk {
    initialize_params {
      image = module.gce-container.source_image
      size = var.gce_processor_disk
    }
  }

  network_interface {
    network = "default"
    subnetwork = "default"
    access_config {}
  }

  metadata = {
    gce-container-declaration = module.gce-container.metadata_value
    google-logging-enabled = "true"
    google-monitoring-enabled = "true"
  }

  scheduling {
    automatic_restart = false
    preemptible = false
  }

  service_account {
    email  = google_service_account.gce-sa.email
    scopes = ["cloud-platform"]
  }

  depends_on = [google_project_service.compute, google_pubsub_subscription.large-simulations-sub, google_service_account.gce-sa]
}
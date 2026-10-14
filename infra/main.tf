terraform {
  required_version = ">= 1.6.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  datasets = ["raw", "staging", "intermediate", "marts"]
  labels = {
    project = "market-data-platform"
  }
}

resource "google_bigquery_dataset" "datasets" {
  for_each   = toset(local.datasets)
  dataset_id = "${var.dataset_prefix}_${each.value}"
  location   = var.bq_location
  labels     = merge(local.labels, { layer = each.value })
}

resource "google_storage_bucket" "raw" {
  name                        = "${var.project_id}-${var.dataset_prefix}-raw"
  location                    = var.bq_location
  uniform_bucket_level_access = true
  force_destroy               = true
  labels                      = local.labels
}

resource "google_service_account" "dbt" {
  account_id   = "${var.dataset_prefix}-dbt"
  display_name = "market-data-platform dbt runner"
}

resource "google_project_iam_member" "dbt_bigquery_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.dbt.email}"
}

resource "google_project_iam_member" "dbt_bigquery_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.dbt.email}"
}

resource "google_storage_bucket_iam_member" "dbt_object_admin" {
  bucket = google_storage_bucket.raw.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.dbt.email}"
}

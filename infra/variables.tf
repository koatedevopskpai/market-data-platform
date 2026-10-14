variable "project_id" {
  description = "GCP project id to deploy into."
  type        = string
}

variable "region" {
  description = "Default GCP region for regional resources."
  type        = string
  default     = "europe-west2"
}

variable "bq_location" {
  description = "BigQuery / GCS location (multi-region, e.g. EU or US)."
  type        = string
  default     = "EU"
}

variable "dataset_prefix" {
  description = "Prefix for BigQuery datasets and the dbt service account."
  type        = string
  default     = "market_data"
}

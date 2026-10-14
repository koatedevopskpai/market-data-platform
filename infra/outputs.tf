output "dataset_ids" {
  description = "Created BigQuery dataset ids, keyed by layer."
  value       = { for name, ds in google_bigquery_dataset.datasets : name => ds.dataset_id }
}

output "raw_bucket" {
  description = "GCS bucket used to stage raw loads."
  value       = google_storage_bucket.raw.name
}

output "dbt_service_account" {
  description = "Service account email for the dbt runner."
  value       = google_service_account.dbt.email
}

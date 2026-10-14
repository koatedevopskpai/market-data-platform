"""Load normalised market data into BigQuery (CSV -> GCS -> BigQuery).

The ``google-cloud`` imports are deferred into the function body so this module
can be imported and unit-tested without GCP dependencies installed.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def load_csv_to_bigquery(
    csv_path: Path,
    project: str,
    table: str,
    dataset: str = "market_data",
    bucket: str | None = None,
    location: str = "EU",
) -> int:
    """Load a CSV into a BigQuery table, optionally staging it via GCS.

    Returns the resulting row count.
    """
    from google.cloud import bigquery, storage

    client = bigquery.Client(project=project)
    destination = f"{project}.{dataset}.{table}"
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    if bucket:
        storage_client = storage.Client(project=project)
        blob = storage_client.bucket(bucket).blob(f"raw/{table}.csv")
        blob.upload_from_filename(str(csv_path))
        uri = f"gs://{bucket}/raw/{table}.csv"
        load_job = client.load_table_from_uri(
            destination, uri, job_config=job_config, location=location
        )
    else:
        with csv_path.open("rb") as handle:
            load_job = client.load_table_from_file(
                handle, destination, job_config=job_config, location=location
            )

    load_job.result()
    return int(client.get_table(destination).num_rows)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Load a CSV into BigQuery.")
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--dataset", default="market_data")
    parser.add_argument("--table", required=True)
    parser.add_argument("--bucket", default=None)
    parser.add_argument("--location", default="EU")
    args = parser.parse_args(argv)

    rows = load_csv_to_bigquery(
        args.csv, args.project, args.table, args.dataset, args.bucket, args.location
    )
    print(f"Loaded {rows} rows into {args.project}.{args.dataset}.{args.table}")


if __name__ == "__main__":
    main()

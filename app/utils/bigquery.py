# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import google.auth
from google.cloud import bigquery

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)


def get_client() -> bigquery.Client:
    """Initializes and returns a BigQuery client."""
    return bigquery.Client()


def list_tables(dataset_id: str) -> list[str]:
    """Lists all tables in a BigQuery dataset.

    Args:
        dataset_id: The ID of the BigQuery dataset.

    Returns:
        A list of table IDs in the dataset.
    """
    client = get_client()
    tables = client.list_tables(dataset_id)
    return [table.table_id for table in tables]


def get_table_schema(dataset_id: str, table_id: str) -> dict:
    """Gets the schema of a BigQuery table.

    Args:
        dataset_id: The ID of the BigQuery dataset.
        table_id: The ID of the BigQuery table.

    Returns:
        A dictionary representing the table schema.
    """
    client = get_client()
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)
    return [{"name": field.name, "type": field.field_type, "mode": field.mode} for field in table.schema]


def execute_query(query: str) -> list[dict]:
    """Executes a BigQuery query and returns the results.

    Args:
        query: The BigQuery query to execute.

    Returns:
        A list of dictionaries representing the query results.
    """
    client = get_client()
    query_job = client.query(query)
    results = query_job.result()
    return [dict(row) for row in results]


def dry_run_query(query: str) -> dict:
    """Performs a dry run of a BigQuery query to validate it and estimate cost.

    Args:
        query: The BigQuery query to validate.

    Returns:
        A dictionary containing the query status and the estimated bytes to be processed.
    """
    client = get_client()
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    query_job = client.query(query, job_config=job_config)
    return {"status": query_job.state, "total_bytes_processed": query_job.total_bytes_processed}

def list_datasets() -> list[str]:
    """Lists all datasets in the project."""
    client = get_client()
    datasets = list(client.list_datasets())
    return [dataset.dataset_id for dataset in datasets]

def list_all_tables_in_project() -> list[str]:
    """Lists all tables in the project, formatted as `dataset.table`."""
    client = get_client()
    datasets = list(client.list_datasets())
    all_tables = []
    for dataset in datasets:
        tables = client.list_tables(dataset.dataset_id)
        for table in tables:
            all_tables.append(f"{dataset.dataset_id}.{table.table_id}")
    return all_tables

def find_column_in_tables(dataset_id: str, column_name: str) -> list[str]:
    """Finds tables in a dataset that contain a specific column.

    Args:
        dataset_id: The ID of the BigQuery dataset.
        column_name: The name of the column to search for.

    Returns:
        A list of table IDs that contain the specified column.
    """
    client = get_client()
    tables = client.list_tables(dataset_id)
    tables_with_column = []
    for table in tables:
        table_ref = client.dataset(dataset_id).table(table.table_id)
        table_schema = client.get_table(table_ref).schema
        for field in table_schema:
            if field.name.lower() == column_name.lower():
                tables_with_column.append(table.table_id)
                break
    return tables_with_column

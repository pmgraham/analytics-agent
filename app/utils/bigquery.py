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
import logging

import google.auth
from google.cloud import bigquery

logger = logging.getLogger(__name__)

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
    logger.info(f"Calling list_tables with dataset_id: {dataset_id}")
    client = get_client()
    tables = client.list_tables(dataset_id)
    result = [table.table_id for table in tables]
    logger.info(f"list_tables returned: {result}")
    return result


def get_table_schema(dataset_id: str, table_id: str) -> dict:
    """Gets the schema of a BigQuery table.

    Args:
        dataset_id: The ID of the BigQuery dataset.
        table_id: The ID of the BigQuery table.

    Returns:
        A dictionary representing the table schema.
    """
    logger.info(f"Calling get_table_schema with dataset_id: {dataset_id}, table_id: {table_id}")
    client = get_client()
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref)
    result = [{"name": field.name, "type": field.field_type, "mode": field.mode} for field in table.schema]
    logger.info(f"get_table_schema returned: {result}")
    return result


def execute_query(query: str) -> list[dict]:
    """Executes a BigQuery query and returns the results.

    Args:
        query: The BigQuery query to execute.

    Returns:
        A list of dictionaries representing the query results.
    """
    logger.info(f"Calling execute_query with query: {query}")
    client = get_client()
    query_job = client.query(query)
    results = query_job.result()
    result = [dict(row) for row in results]
    logger.info(f"execute_query returned: {result}")
    return result


def dry_run_query(query: str) -> dict:
    """Performs a dry run of a BigQuery query to validate it and estimate cost.

    Args:
        query: The BigQuery query to validate.

    Returns:
        A dictionary containing the query status and the estimated bytes to be processed.
    """
    logger.info(f"Calling dry_run_query with query: {query}")
    client = get_client()
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    query_job = client.query(query, job_config=job_config)
    result = {"status": query_job.state, "total_bytes_processed": query_job.total_bytes_processed}
    logger.info(f"dry_run_query returned: {result}")
    return result

def list_datasets() -> list[str]:
    """Lists all datasets in the project."""
    logger.info("Calling list_datasets")
    client = get_client()
    datasets = list(client.list_datasets())
    result = [dataset.dataset_id for dataset in datasets]
    logger.info(f"list_datasets returned: {result}")
    return result

def list_queryable_resources_in_project() -> list[str]:
    """Lists all queryable resources (tables, views, materialized views) in the project, formatted as `dataset.resource`."""
    logger.info("Calling list_queryable_resources_in_project")
    client = get_client()
    datasets = list(client.list_datasets())
    all_resources = []
    for dataset in datasets:
        tables = client.list_tables(dataset.dataset_id)
        for table in tables:
            all_resources.append(f"{dataset.dataset_id}.{table.table_id}")
    logger.info(f"list_queryable_resources_in_project returned: {all_resources}")
    return all_resources

def list_datasets_with_queryable_resources() -> list[str]:
    """Lists all datasets in the project that contain at least one queryable resource (table, view, or materialized view)."""
    logger.info("Calling list_datasets_with_queryable_resources")
    client = get_client()
    datasets = list(client.list_datasets())
    datasets_with_resources = []
    for dataset in datasets:
        tables = list(client.list_tables(dataset.dataset_id))
        if tables:
            datasets_with_resources.append(dataset.dataset_id)
    logger.info(f"list_datasets_with_queryable_resources returned: {datasets_with_resources}")
    return datasets_with_resources

def find_column_in_tables(dataset_id: str, column_name: str) -> list[str]:
    """Finds tables in a dataset that contain a specific column.

    Args:
        dataset_id: The ID of the BigQuery dataset.
        column_name: The name of the column to search for.

    Returns:
        A list of table IDs that contain the specified column.
    """
    logger.info(f"Calling find_column_in_tables with dataset_id: {dataset_id}, column_name: {column_name}")
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
    logger.info(f"find_column_in_tables returned: {tables_with_column}")
    return tables_with_column

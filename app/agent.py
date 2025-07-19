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
from google.adk.agents import Agent
from app.utils.bigquery import (
    list_datasets_with_queryable_resources,
    list_queryable_resources_in_project,
    get_table_schema,
    execute_query,
    dry_run_query,
    find_column_in_tables,
)

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-pro",
    instruction="""You are a BigQuery expert for a team of analysts. Your goal is to be as helpful as possible and not assume the user knows the data structure. You have access to a variety of tools to help you answer questions about BigQuery datasets.

Here is your workflow:
1.  When the user asks a question, first try to infer the queryable resource (table, view, or materialized view) to use.
2.  If you are unsure which resource to use, use the `list_queryable_resources_in_project` tool to get a list of all available resources.
3.  You can also use the `list_datasets_with_queryable_resources` tool to get a list of all datasets that contain at least one queryable resource.
4.  Present the user with a list of all the resources you found, and ask them to choose one.
5.  Once the user has selected a resource, you should construct the SQL query required to answer the user's question.
6.  You should then validate the SQL syntax and perform a dry run to ensure that the query will not fail.
7.  If the dry run is successful, you should execute the query and return the results to the user in a table format. You should also present the SQL query you used in a nicely formatted code block.
8.  If the dry run fails, you should try to correct the SQL query and try again. If you are unable to correct the query, you should inform the user of the error and ask for clarification.

Important: When using regular expressions in a query, you must not have more than one capturing group in the expression. If you need to extract multiple parts from a single column, use a separate function call for each part (e.g., one REGEXP_EXTRACT for address, another for city, etc.). Do not use the `REGEXP_QUOTE` function as it is not supported.""",
    tools=[
        list_datasets_with_queryable_resources,
        list_queryable_resources_in_project,
        get_table_schema,
        execute_query,
        dry_run_query,
        find_column_in_tables,
    ],
)

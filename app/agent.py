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
from google.adk.agents.callback_context import CallbackContext
from app.utils.bigquery import (
    list_datasets_with_queryable_resources,
    list_queryable_resources_in_project,
    get_table_schema,
    execute_query,
    dry_run_query,
)

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

from google.adk.tools import ToolContext
from app.tools import generate_python_code

def before_tool_callback(tool_context: ToolContext, tool, args):
    tool_name = tool.name
    print(f"Calling tool: {tool_name} with args: {args}")

def after_tool_callback(tool_context: ToolContext, tool, args, tool_response):
    tool_name = tool.name
    print(f"Finished calling tool: {tool_name} with args: {args}, response: {tool_response}")

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-pro",
    instruction="""You are a BigQuery expert for a team of analysts. Your goal is to be as helpful as possible and not assume the user knows the data structure. You have access to a variety of tools to help you answer questions about BigQuery datasets.

Here is your workflow:
1.  **ALWAYS** start by using `list_datasets_with_queryable_resources` to identify available datasets.
2.  Then, use `list_queryable_resources_in_project` to get a list of all available tables and views within those datasets.
3.  Present the user with a list of all the resources you found, and ask them to choose one.
4.  Once the user has selected a resource, you should construct the SQL query required to answer the user's question.
5.  You should then validate the SQL syntax and perform a dry run to ensure that the query will not fail.
6.  If the dry run is successful, you should execute the query and return the results to the user in a table format. You should also present the SQL query you used in a nicely formatted code block.
7.  If the dry run fails, you should try to correct the SQL query and try again. If you are unable to correct the query, you should inform the user of the error and ask for clarification.
8.  Always limit queries to no more than 10 rows unless the queries contain aggregrates (e.g., COUNT(*), SUM(column), etc.).
9.  Always show the query before showing the results.
10. Always show results in markdown format.
11. Always limit your answers to BigQuery or things directly related to BigQuery.
12. When asked to generate Python code for BigQuery data analysis, use the `generate_python_code` tool. Prioritize Polars for dataframe operations. Only use Pandas if the request specifically mentions BigFrames or implies a need for BigFrames functionality.

Examples of things you should answer because they directly relate to BigQuery:
    Cloud Storage
    Pub/Sub
    Cloud Composer
    Dataflow
    Vertex AI
    Data Fusion
    Looker Studio
    BigQuery ML
    BigTable
    Spanner
    Cloud Functions
    Cloud SQL (especially for things like query federation)
    Datastream
    Dataplex
    Looker
    Any service native to BigQuery like BI Engine, Data Transfer Service, Dataprep, Pipelines, Data Canvas, etc.

Important: When using regular expressions in a query, you must not have more than one capturing group in the expression. If you need to extract multiple parts from a single column, use a separate function call for each part (e.g., one REGEXP_EXTRACT for address, another for city, etc.). Do not use the `REGEXP_QUOTE` function as it is not supported.""",
    tools=[
        list_datasets_with_queryable_resources,
        list_queryable_resources_in_project,
        get_table_schema,
        execute_query,
        dry_run_query,
        generate_python_code,
    ],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)

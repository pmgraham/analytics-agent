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
    list_datasets,
    list_tables,
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
    model="gemini-2.5-flash",
    instruction="""You are a BigQuery expert. You have access to a variety of tools to help you answer questions about BigQuery datasets.

Here are the tools you have access to:
- `list_datasets`: Lists all datasets in the project.
- `list_tables`: Lists all tables in a BigQuery dataset.
- `get_table_schema`: Gets the schema of a BigQuery table.
- `dry_run_query`: Performs a dry run of a BigQuery query to validate it and estimate cost.
- `execute_query`: Executes a BigQuery query and returns the results.
- `find_column_in_tables`: Finds tables in a dataset that contain a specific column.

When a user asks a question, you should first try to infer the table or tables to use. If you are unsure, you should list the available tables and ask the user to choose one.

Once you have the table, you should construct the SQL query required to answer the user's question. You should then validate the SQL syntax and perform a dry run to ensure that the query will not fail.

If the dry run is successful, you should execute the query and return the results to the user in a table format. You should also present the SQL query you used in a nicely formatted code block.

If the dry run fails, you should try to correct the SQL query and try again. If you are unable to correct the query, you should inform the user of the error and ask for clarification.""",
    tools=[
        list_datasets,
        list_tables,
        get_table_schema,
        execute_query,
        dry_run_query,
        find_column_in_tables,
    ],
)

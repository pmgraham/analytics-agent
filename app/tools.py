from google.adk.tools import ToolContext

def generate_python_code(description: str, tool_context: ToolContext) -> str:
    """Generates Python code for BigQuery data analysis, prioritizing Polars for dataframes.
    Use this tool when the user asks for Python code examples related to BigQuery data.
    Default to Polars for dataframe operations. Only use Pandas if the request specifically
    mentions BigFrames or implies a need for BigFrames functionality.

    Args:
        description (str): A detailed description of the Python code to generate,
                           including the BigQuery table/dataset and the desired analysis.
    Returns:
        str: The generated Python code.
    """
    # Placeholder implementation
    if "bigframes" in description.lower():
        return f"""
import bigframes.pandas as bfp
from google.cloud import bigquery

# Example using BigFrames for: {description}
client = bigquery.Client()
# Replace with your actual project, dataset, and table
df = bfp.read_gbq("your_project.your_dataset.your_table")
print(df.head())
"""
    else:
        return f"""
import polars as pl
from google.cloud import bigquery

# Example using Polars for: {description}
client = bigquery.Client()
# Replace with your actual project, dataset, and table
query = '''
SELECT *
FROM `your_project.your_dataset.your_table`
LIMIT 100
'''
df = pl.read_database(query, connection=client)
print(df.head())
"""

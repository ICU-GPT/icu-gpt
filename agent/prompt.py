from langchain.prompts.prompt import PromptTemplate

COMPLETION_PROMPT = "If everything looks good, respond with APPROVED"

USER_PROXY_PROMPT = (
            "You are icugpt agent"
            + COMPLETION_PROMPT
        )
DB_PROMPT = (
            "Data Engineer Generate the initial SQL based on the prompt input. Send it to the Data Analyst to be run sql."
            + COMPLETION_PROMPT
        )
DATA_PROMPT = (
            "Data Analyst, You run the SQL query, generate the response and send it client."
            + COMPLETION_PROMPT
        )

PROMPT_SUFFIX = """Only use the following tables:
{table_info}

Question: {input}"""

_postgres_prompt = """You are a PostgreSQL expert. Given an input question, Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in double quotes (") to denote them as delimited identifiers.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
Pay attention to use CURRENT_DATE function to get the current date, if the question involves "today".

Use the following format:
Question: Question here
SQLQuery: SQL Query to run
"""

POSTGRES_PROMPT = PromptTemplate(
    input_variables=["input", "table_info"],
    template=_postgres_prompt + PROMPT_SUFFIX,
)
from datetime import date, datetime
import mysql.connector
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import LlmAgent
from dotenv import load_dotenv
import os

load_dotenv()

host = os.getenv('HOST')
user = os.getenv("USER")
password = os.getenv("PASSWORD")
database = os.getenv("DATABASE")


def get_result(query: str) -> dict:
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            for key, value in row.items():
                if isinstance(value, (date, datetime)):
                    row[key] = value.isoformat()

        return {"rows": result}

    except mysql.connector.Error as err:
        return {"error": str(err)}

    finally:
        cursor.close()
        connection.close()


sql_agent = LlmAgent(
    model=LiteLlm(
        api_base='https://openrouter.ai/api/v1',
        model='openrouter/openai/gpt-oss-120b',
        api_key='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'
    ),
    name="sql_agent",
    description="Executes SQL on database using get_result tool",
    instruction="""
        You are an expert data analyst for the MySQL Employee Sample Database.

        You have full access to the following tables:
        1. employees
        2. departments
        3. dept_emp
        4. dept_manager
        5. titles
        6. salaries
        And the following views:
        7. dept_emp_latest_date
        8. current_dept_emp

        Your job:
        1. Convert the user’s natural language question into the most accurate SQL query.
        2. Use ALL relevant tables or views to answer the question, not just the employees table.
           - Join tables when needed (e.g., employees + salaries, employees + departments, etc.)
           - Always choose the correct table(s) based on the question.
        3. Always include LIMIT 50 unless the user clearly specifies otherwise.
        4. If the user asks for “all” rows, DO NOT execute the query.
           Instead reply: “The dataset is too large to return all rows. Please specify a LIMIT.”
        5. Use get_result(query) to execute SQL and retrieve results.
        6. Present the final answer in a clean, readable table format.
        7. Only generate valid MySQL queries. 
        8. If the query is not related to sql database redirect the user prompt to root agent.
        9. Always show the user what query you have used to get the data.""",
    tools=[get_result]
)

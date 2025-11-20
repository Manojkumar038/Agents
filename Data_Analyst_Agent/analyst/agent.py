import mysql.connector
from google.adk.agents.llm_agent import Agent


def get_result(query: str) -> dict:
    """
    Executes SQL query on Aiven DB and returns rows as dictionaries.
    """
    connection = mysql.connector.connect(
        host="mysql-126f641c-agent11.e.aivencloud.com",
        port=25229,
        user="avnadmin",
        password="AVNS_nwa2oWCGHR41bpn0qze",
        database="defaultdb",
        ssl_ca="/content/ca.pem"
    )

    cursor = connection.cursor(dictionary=True)  # IMPORTANT
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return {"rows": result}

    except mysql.connector.Error as err:
        return {"error": str(err)}

    finally:
        cursor.close()
        connection.close()


root_agent = Agent(
    root_agent=Agent(
        model="gemini-2.5-flash",
        name="analyst",
        description="Executes SQL on database using get_result tool",
        instruction="""
            You are an expert data analyst.

            1. Convert user natural language to SQL.
            2. Call get_result(query) to execute.
            3. Present a clean summary of the results to the user in the form of table.
            Only generate valid MySQL queries.
        """,
        tools=[get_result]
    )
)

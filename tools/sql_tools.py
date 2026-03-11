from datetime import date, datetime
import mysql.connector
import os

from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

host = os.getenv("HOST")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
database = os.getenv("DATABASE")

print(host, user, password, database)

@tool
def get_database_schema() -> str:
    """
    Returns all tables and columns in the database.
    Use this before writing SQL queries.
    """

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        cursor = connection.cursor()

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        schema = ""

        for (table_name,) in tables:
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()

            schema += f"\nTable: {table_name}\n"

            for col in columns:
                schema += f"  {col[0]} ({col[1]})\n"

        cursor.close()
        connection.close()

        return schema

    except mysql.connector.Error as err:
        return f"Schema error: {err}"


@tool
def query_sql_database(query: str) -> str:
    """
    Execute a SQL query on the MySQL database and return results.
    Use this tool whenever the user asks about database information.
    """

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        cursor = connection.cursor(dictionary=True)

        cursor.execute(query)
        result = cursor.fetchall()

        for row in result:
            for key, value in row.items():
                if isinstance(value, (date, datetime)):
                    row[key] = value.isoformat()

        cursor.close()
        connection.close()

        return str(result)

    except mysql.connector.Error as err:
        return f"SQL Error: {err}"
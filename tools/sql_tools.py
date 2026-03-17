from datetime import date, datetime
import re
import mysql.connector
import os

from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

host = os.getenv("HOST")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
database = os.getenv("DATABASE")

LIMIT = 30

LAST_QUERY = None
OFFSET = 0


def enforce_limit(query: str) -> str:

    # if query already contains LIMIT, keep it
    if re.search(r"\blimit\b", query, re.IGNORECASE):
        return query

    query = query.rstrip(";")

    return f"{query} LIMIT {LIMIT}"

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
    Supports pagination.
    """

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        cursor = connection.cursor(dictionary=True)

        global LAST_QUERY
        global OFFSET

        q = query.lower().strip()

        # pagination request
        if any(word in q for word in ["next", "more"]):

            if not LAST_QUERY:
                return "There is no previous query to paginate."

            OFFSET += LIMIT
            query = f"{LAST_QUERY} LIMIT {LIMIT} OFFSET {OFFSET}"

        else:
            OFFSET = 0
            query = enforce_limit(query)

            LAST_QUERY = query.replace(f" LIMIT {LIMIT}", "")

        cursor.execute(query)

        result = cursor.fetchall()

        for row in result:
            for key, value in row.items():
                if isinstance(value, (date, datetime)):
                    row[key] = value.isoformat()

        cursor.close()
        connection.close()

        return {
            "start": OFFSET + 1,
            "end": OFFSET + len(result),
            "rows": result
        }

    except mysql.connector.Error as err:
        return f"SQL Error: {err}"
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

from tools.sql_tools import query_sql_database


def create_sql_agent():

    llm = ChatOllama(
        model="qwen2.5:3b",
        temperature=0
    )

    tools = [query_sql_database]

    schema = """
Database: employees

Tables:

employees(
 emp_no INT PRIMARY KEY,
 birth_date DATE,
 first_name VARCHAR(14),
 last_name VARCHAR(16),
 gender ENUM('M','F'),
 hire_date DATE
)

departments(
 dept_no CHAR(4) PRIMARY KEY,
 dept_name VARCHAR(40)
)

dept_emp(
 emp_no INT,
 dept_no CHAR(4),
 from_date DATE,
 to_date DATE
)

salaries(
 emp_no INT,
 salary INT,
 from_date DATE,
 to_date DATE
)

titles(
 emp_no INT,
 title VARCHAR(50),
 from_date DATE,
 to_date DATE
)

Relationships:
employees.emp_no = dept_emp.emp_no
departments.dept_no = dept_emp.dept_no
employees.emp_no = salaries.emp_no
employees.emp_no = titles.emp_no
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         f"""
You are a MySQL expert.

Database schema:

{schema}

Rules:
- Only use the tables and columns defined above.
- Do NOT invent columns.
- Use proper JOINs when required.
- When querying employees by department, join:
  employees → dept_emp → departments.

Workflow:
1. Write the SQL query.
2. Execute it using query_sql_database.
3. Return the results clearly if the query result is too big to show just give the few lines from the starting and ending and ask if the user wants any pdf to download the complete result.
"""),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True
    )

    return executor
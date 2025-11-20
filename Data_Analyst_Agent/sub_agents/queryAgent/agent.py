from google.adk.agents.llm_agent import Agent
import os
import mysql.connector
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents import AgentType

load_dotenv()


def establish_database_connection():
    conn = mysql.connector.connect(
        host="mysql-126f641c-agent11.e.aivencloud.com",
        port=25229,
        user="avnadmin",
        password="AVNS_nwa2oWCGHR41bpn0qze",
        database="defaultdb",
        ssl_ca="./ca.pem"
    )
    return conn


db_uri = (
    "mysql+mysqlconnector://avnadmin:"
    "AVNS_nwa2oWCGHR41bpn0qze"
    "@mysql-126f641c-agent11.e.aivencloud.com:25229/"
    "defaultdb"
    "?ssl_ca=/content/ca.pem"
)

db = SQLDatabase.from_uri(db_uri)

model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0
)

agent = create_sql_agent(
    llm=model,
    db=db,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

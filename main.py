from graph.workflow import build_graph
import os
from langchain_core.messages import HumanMessage


host = os.getenv("HOST")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
database = os.getenv("DATABASE")

graph = build_graph()

config = {"configurable": {"thread_id": "user1"}}

while True:

    query = input("\nUser: ")

    result = graph.invoke(
    {"messages": [HumanMessage(content=query)]},
    config=config
    )

    print("\nAssistant:", result["messages"][-1].content)
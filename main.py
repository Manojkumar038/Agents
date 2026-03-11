from graph.workflow import build_graph
import os

host = os.getenv("HOST")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
database = os.getenv("DATABASE")

print(host, user, password, database)

graph = build_graph()

while True:

    query = input("\nUser: ")

    result = graph.invoke({
        "query": query
    })

    print("\nAssistant:", result["result"])
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama

from agents.root_agent import route_query
from agents.sql_agent import create_sql_agent


sql_agent = create_sql_agent()


class State(TypedDict):
    query: str
    route: str
    result: str


def router_node(state: State):

    route = route_query(state["query"])

    return {"route": route}


def sql_node(state: State):

    result = sql_agent.invoke({
        "input": state["query"]
    })

    return {"result": result["output"]}



llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0
)

def general_node(state: State):

    response = llm.invoke(state["query"])

    return {"result": response.content}


def build_graph():

    graph = StateGraph(State)

    graph.add_node("router", router_node)
    graph.add_node("sql_agent", sql_node)
    graph.add_node("general", general_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        lambda state: state["route"],
        {
            "sql_agent": "sql_agent",
            "general": "general"
        }
    )

    graph.add_edge("sql_agent", END)
    graph.add_edge("general", END)

    return graph.compile()
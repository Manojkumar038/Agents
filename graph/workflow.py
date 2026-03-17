from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, AIMessage
import json
from agents.root_agent import route_query
from agents.sql_agent import create_sql_agent
from tools.sql_tools import query_sql_database

from langgraph.checkpoint.memory import MemorySaver

sql_agent = create_sql_agent()


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    route: str
    sql_query: str
    offset: int
    last_query: str

def is_next_page(query: str):
    q = query.lower()
    return "next" in q or "more" in q or "next page" in q


def router_node(state: State):

    query = state["messages"][-1].content
    route = route_query(query)

    return {"route": route}


def sql_generator_node(state: State):

    query = state["messages"][-1].content

    response = llm.invoke(
        f"""
        Generate a SQL query for this request.

        IMPORTANT RULES:
        - Do not include LIMIT
        - Only return SQL
        - Request: {query}
        """
    )

    return {"sql_query": response.content}


LIMIT = 30

def sql_node(state: State):

    user_query = state["messages"][-1].content.lower()

    last_query = state.get("last_query")
    offset = state.get("offset", 0)

    if is_next_page(user_query) and last_query:

        offset += LIMIT
        sql_query = f"{last_query} LIMIT {LIMIT} OFFSET {offset}"

    else:

        result = sql_agent.invoke({
            "input": user_query
        })

        sql_query = result["intermediate_steps"][0][0].tool_input["query"]

        last_query = sql_query
        offset = 0

        sql_query = f"{sql_query} LIMIT {LIMIT}"

    result = query_sql_database.invoke({
        "query": sql_query
    })

    return {
        "messages": [AIMessage(content=json.dumps(result))],
        "last_query": last_query,
        "offset": offset
    }


llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0
)

from langchain_core.messages import SystemMessage

def general_node(state: State):

    messages = [
        SystemMessage(
            content="You are a helpful assistant. Always remember the conversation history when answering."
        )
    ] + state["messages"]

    response = llm.invoke(messages)

    return {
        "messages": [response]
    }


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

    memory = MemorySaver()

    return graph.compile(checkpointer=memory)
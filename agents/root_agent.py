from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0
)


def route_query(query: str):

    prompt = f"""
        You are a routing agent.

        Agents:
        - sql_agent → questions about database tables or data
        - general → everything else

        Return only the agent name.

        Question: {query}
    """

    response = llm.invoke(prompt)

    return response.content.strip().lower()
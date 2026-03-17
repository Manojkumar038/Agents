from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from graph.workflow import build_graph
from langchain_core.messages import HumanMessage

app = FastAPI()

# Enable CORS so React can call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()

config = {"configurable": {"thread_id": "user1"}}


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatRequest):

    result = graph.invoke(
        {"messages": [HumanMessage(content=req.message)]},
        config=config
    )

    response = result["messages"][-1].content

    return {"response": response}
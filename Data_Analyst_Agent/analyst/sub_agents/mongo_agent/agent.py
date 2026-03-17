from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import LlmAgent
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()

# MongoDB configuration
mongo_uri = os.getenv("MONGO_URI")


def convert_types(doc):
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, dict):
            convert_types(value)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, ObjectId):
                    value[i] = str(item)
                elif isinstance(item, dict):
                    convert_types(item)
    return doc


def get_result(params: dict) -> dict:
    collection = params["collection"]
    operation = params["operation"]
    query = params.get("query", {})

    client = MongoClient(mongo_uri)
    db = client["sample_mflix"]
    col = db[collection]

    try:
        if operation == "find":
            docs = list(col.find(query).limit(50))
            return [convert_types(d) for d in docs]

        elif operation == "aggregate":
            docs = list(col.aggregate(query))
            return [convert_types(d) for d in docs]

        elif operation == "insert":
            result = col.insert_one(query)
            return {"inserted_id": str(result.inserted_id)}

        elif operation == "update":
            result = col.update_one(query["filter"], {"$set": query["update"]})
            return {"matched": result.matched_count, "modified": result.modified_count}

        elif operation == "delete":
            result = col.delete_one(query)
            return {"deleted": result.deleted_count}

        else:
            return {"error": "Unsupported operation"}

    except Exception as err:
        return {"error": str(err)}


mongo_agent = LlmAgent(
    model=LiteLlm(
        api_base='https://openrouter.ai/api/v1',
        model='openrouter/openai/gpt-oss-120b',
        api_key='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'
    ),
    name='mongo_agent',
    description='A helpful MongoDB expert that executes queries on sample_mflix.',
    instruction="""   # <-- FIXED THIS LINE
        You are a MongoDB query expert.

        Your responsibilities:

        1. Based on the user's request, generate a MongoDB query in the following JSON format:

        {
          "collection": "<collection_name>",
          "operation": "<find | insert | update | delete | aggregate>",
          "query": { ... }
        }

        Rules:
        - Always choose the correct MongoDB collection from the sample_mflix database 
          (movies, comments, users, theaters, sessions).
        - Always include a filter in "query".
        - For find operations, do NOT include limit, sort, or projection — these are handled automatically.
        - If the user requests “all results”, DO NOT execute a large query. 
          Respond: "The dataset is too large to return all rows. Please specify a LIMIT."

        2. After generating the JSON, call get_result({ ... }) to execute it.

        3. Present the results in a clean table.

        4. Only generate valid MongoDB queries that match the schema of sample_mflix.
    """,
    tools=[get_result]
)

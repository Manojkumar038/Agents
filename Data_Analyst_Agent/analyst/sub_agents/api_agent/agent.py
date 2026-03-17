from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
import requests
from typing import Dict, List, Any

BASE_URL = "https://fakestoreapi.com"


def get_product_details() -> List[Dict[str, Any]]:
    """
    Fetch all product details from Fake Store API.
    Returns a list of products with title, price, description, category, and rating.
    """
    try:
        response = requests.get(BASE_URL + "/products", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return [{"error": str(e)}]


def get_single_product_details(product_id: int) -> Dict[str, Any]:
    """
    Fetch a single product by ID from Fake Store API.
    Product ID must be between 1 and 20.
    """
    try:
        response = requests.get(f"{BASE_URL}/products/{product_id}", timeout=5)

        if response.status_code == 404:
            return {"error": f"Product with ID {product_id} not found"}

        response.raise_for_status()

        if not response.text.strip():
            return {"error": "Empty response from API"}

        return response.json()

    except requests.RequestException as e:
        return {"error": str(e)}


def add_product(title: str, price: float) -> Dict[str, Any]:
    """
    Add a new product to Fake Store API.
    Requires title and price.
    """
    payload = {
        "title": title,
        "price": price
    }

    try:
        response = requests.post(BASE_URL + "/products", json=payload, timeout=5)
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        return {"error": str(e)}


api_agent = Agent(
    model=LiteLlm(
        api_base='https://openrouter.ai/api/v1',
        model='openrouter/openai/gpt-oss-120b',
        api_key='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'
    ),
    name="api_agent",
    description="Handles product queries and product creation using Fake Store API.",
    instruction="""
    You are an API specialist agent.

    Use tools to answer user questions about products.

    When user asks to:
    - List products → call get_product_details
    - Get product by ID → call get_single_product_details
    - Add a product → call add_product and collect title and price

    Always summarize results clearly.
    """,
    tools=[get_product_details, get_single_product_details, add_product],
)

import logging
import os

import dotenv
import httpx
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

# Load environment variables from .env file
dotenv_path = os.path.join(os.getcwd(), ".env")
dotenv.load_dotenv(dotenv_path)

# Tavily Search API Credentials
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


class ToolKit:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    @tool
    async def retrieve_from_vector_database(prompt):
        """Retrieves the relevant context from a vector database for a given prompt."""
        # Define the headers and payload for the HTTP request
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "query": str(prompt),
            "search_strategy": "vector-search",
            "n_results": 5
        }

        try:
            # Make the HTTP request to the vector database API
            async with httpx.AsyncClient() as client:
                response = await client.post("http://localhost:8001/retrieve-context", json=payload, headers=headers)
            
            # Log the status code and response content
            logging.info(f"retrieve_context_response status: {response.status_code}")
            logging.info(f"retrieve_context_response content: {response.json()}")

            # Check if the request was successful
            response.raise_for_status()
            
            # Return the response content if the request was successful
            return response.json()

        except httpx.RequestError as e:
            # Log the error if there was an issue with the request
            logging.error(f"An error occurred while requesting: {e}")
            return {"error": "An error occurred while trying to retrieve context from the vector database."}

        except httpx.HTTPStatusError as e:
            # Log the error if the response status code indicates an error
            logging.error(f"HTTP error occurred: {e.response.status_code} - {e.response.content}")
            return {"error": "Received an error response from the vector database."}

        except Exception as e:
            # Log any other exceptions that may occur
            logging.error(f"An unexpected error occurred: {e}")
            return {"error": "An unexpected error occurred while retrieving context from the vector database."}
        

    @staticmethod
    @tool
    async def search_with_tavily(prompt):
        """Searches the relevant context on the web through Tavily Search API for a given prompt."""
        tool = TavilySearchResults()
        output = await tool.ainvoke({"query": prompt})
        return output
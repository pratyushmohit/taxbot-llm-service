import logging
from typing import Optional

import httpx
from langchain.schema import HumanMessage
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_experimental.utilities.python import PythonREPL
from langchain_openai import ChatOpenAI

from utils.env_variables import EnvironmentVariables as env


class ToolKit:
    def __init__(self) -> None:
        pass

    @staticmethod
    @tool
    async def classify(prompt: str, chat_history) -> bool:
        """Classifies a new prompt as 'tax-related' or 'non-tax-related' based on chat history (if any)"""
        llm = ChatOpenAI(api_key=env.OPENAI_API_KEY,
                         model_name="gpt-3.5-turbo", max_tokens=5)
        classification_prompt = (
            "Based on the following conversation history, classify the new prompt as 'tax-related' or 'non-tax-related'."
            "Provide only the classification:\n\n"
            f"Conversation history:\n{str(chat_history)}\n\n"
            f"New prompt:\n{prompt}"
        )
        try:
            response = await llm.agenerate(
                messages=[[HumanMessage(content=classification_prompt)]]
            )
            classification = response.generations[0][0].message.content.strip(
            ).lower()
            classification = classification.strip("'")
            logging.info(f"classification: {classification}")
            return classification == "tax-related"

        except Exception as e:
            logging.error(f"Error classifying the prompt: {e}")
            return False

    @staticmethod
    @tool
    async def retrieve_from_vector_database(prompt:str , collection_name: str):
        """Retrieves the relevant context from a vector database for a given prompt from a specified collection."""
        try:
            # Define the headers and payload for the HTTP request
            headers = {
                "Content-Type": "application/json"
            }
            payload = {
                "query": str(prompt),
                "collection_name": collection_name,
                "search_strategy": "vector-search",
                "n_results": 5
            }
            # Make the HTTP request to the vector database API
            async with httpx.AsyncClient() as client:
                response = await client.post(env.RETRIEVE_FROM_VECTOR_DATABASE_ENDPOINT, json=payload, headers=headers)

                # Log the status code and response content
                logging.info(
                    f"retrieve_context_response status: {response.status_code}")

                # Check if the request was successful
                response.raise_for_status()

                output = response.json()

                # Close AsyncClient
                await client.aclose()

            # Return the response content if the request was successful
            return output

        except httpx.RequestError as e:
            # Log the error if there was an issue with the request
            logging.error(f"An error occurred while requesting: {e}")
            return {"error": "An error occurred while trying to retrieve context from the vector database."}

        except httpx.HTTPStatusError as e:
            # Log the error if the response status code indicates an error
            logging.error(
                f"HTTP error occurred: {e.response.status_code} - {e.response.content}")
            return {"error": "Received an error response from the vector database."}

        except Exception as e:
            # Log any other exceptions that may occur
            logging.error(f"An unexpected error occurred: {e}")
            return {"error": "An unexpected error occurred while retrieving context from the vector database."}

    @staticmethod
    @tool
    async def search_with_tavily(prompt: str):
        """Searches the relevant context on the web through Tavily Search API for a given prompt."""
        tool = TavilySearchResults(max_results=2)
        output = await tool.ainvoke({"query": prompt})
        return output
    
    @staticmethod
    @tool
    async def python_repl(prompt):
        """A python tool to generate matplotlib charts"""
        class PythonREPL:
            def run(self, code):
                # Execute the code (In a real implementation, this should be more secure and robust)
                exec(code, globals())
                return locals().get('result', '')
        
        # Sample code to generate a plot
        code = """
                import matplotlib.pyplot as plt
                import numpy as np
                from io import BytesIO
                import base64

                # Generate some data
                x = np.linspace(0, 10, 100)
                y = np.sin(x)

                # Create a plot
                plt.figure()
                plt.plot(x, y)
                plt.title('Sine Wave')
                plt.xlabel('x')
                plt.ylabel('sin(x)')

                # Save the plot to a bytes buffer
                buf = BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)

                # Encode the bytes to base64 string
                img_str = base64.b64encode(buf.read()).decode('utf-8')
                result = img_str
            """
        python_repl = PythonREPL()
        output = python_repl.run(code)
        
        return output

classify = ToolKit.classify
retrieve_from_vector_database = ToolKit.retrieve_from_vector_database
search_with_tavily = ToolKit.search_with_tavily

import json
import logging
import os
import httpx

import dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
dotenv_path = os.path.join(os.getcwd(), ".env")
dotenv.load_dotenv(dotenv_path)

# OpenAI Credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# MongoDB Atlas credentials
DB_URI = os.getenv("MONGO_DB_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")

system_prompts_path = os.path.join(
    os.getcwd(), "src", "prompt_templates", "system_prompts.json")

with open(system_prompts_path, "r") as file:
    system_prompts = json.load(file)


class ConversationalBot:
    def __init__(self):
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompts["1"]),
            ("human", "Previous message history: {history}"),
            ("human", "Related documents: {related_documents}"),
            ("human", "User's new question: {input}"),
        ])
        self.llm = ChatOpenAI(api_key=OPENAI_API_KEY,
                              model_name="gpt-4", max_tokens=1500)
        self.chain = self.prompt_template | self.llm | StrOutputParser()

    async def is_tax_related(self, chat_history: MongoDBChatMessageHistory, prompt, related_documents):
        history_text = "\n".join(
            f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
            for msg in chat_history.messages
        )
        classification_prompt = (
            "Based on the following conversation history and related documents, classify the new prompt as 'tax-related' or 'non-tax-related'."
            "Provide only the classification:\n\n"
            f"Conversation history:\n{history_text}\n\n"
            f"Related documents:\n{related_documents}\n\n"
            f"New prompt:\n{prompt}"
        )
        try:
            response = await self.llm.agenerate(
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

    async def generate(self, session_id, prompt):

        chat_history = MongoDBChatMessageHistory(
            connection_string=DB_URI,
            session_id=session_id,
            database_name=DB_NAME,
            collection_name=f"session-{session_id}",
        )

        # call retrieve_context endpoint and determine similarity score to proceed further
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "query": prompt,
            "search_strategy": "vector-search",
            "n_results": 5
        }
        retrieve_context_response = httpx.post(
            "http://localhost:8001/retrieve-context", json=payload, headers=headers)

        # Log the status code and content of the response
        logging.info(
            f"retrieve_context_response status: {retrieve_context_response.status_code}")
        logging.info(
            f"retrieve_context_response content: {retrieve_context_response.content}")

        # Check if the response is successful and contains JSON
        if retrieve_context_response.status_code == 200:
            try:
                # Parsing the JSON content of the response
                retrieve_context_data = retrieve_context_response.json()

                # Extract and concatenate the content
                related_documents = retrieve_context_data["output"]["documents"]

                # Since documents is a list of lists, we need to extract the content from the inner lists
                related_documents = " ".join(
                    [doc[0] for doc in related_documents])

            except ValueError as e:
                logging.error(f"Error parsing JSON response: {e}")
                # Handle the error or raise an exception
        else:
            logging.error(
                f"Failed to retrieve context: {retrieve_context_response.status_code}")
            related_documents = ""

        is_tax_related = await self.is_tax_related(chat_history, prompt, related_documents)
        logging.info(f"is_tax_related: {is_tax_related}")

        if not is_tax_related:
            return ("I'm sorry, but I can only help with tax-related queries or queries on your tax documents. Please ask a question related to taxes.", [])

        # Add user message to chat history
        await chat_history.aadd_messages([HumanMessage(content=prompt)])

        try:
            # Generate a response using the RunnableSequence
            response = await self.chain.ainvoke({
                "history": chat_history.messages,
                "related_documents": related_documents,
                "input": prompt
            })

            # Add AI message to chat history
            await chat_history.aadd_messages([AIMessage(content=response)])

            # Convert messages to list of dictionaries
            serialized_messages = []
            for msg in chat_history.messages:
                if isinstance(msg, HumanMessage):
                    serialized_messages.append({
                        "role": "human",
                        "content": msg.content
                    })
                elif isinstance(msg, AIMessage):
                    serialized_messages.append({
                        "role": "ai",
                        "content": msg.content
                    })

            return response, serialized_messages

        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return ("An error occurred while processing your request.", [])

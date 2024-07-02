import json
import logging
import os

import dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_openai import ChatOpenAI
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Load environment variables from .env file
dotenv_path = os.path.join(os.getcwd(), ".env")
dotenv.load_dotenv(dotenv_path)

# OpenAI Credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# MongoDB Atlas credentials
DB_URI = os.getenv("MONGO_DB_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")

# Create a new client and connect to the server
client = MongoClient(DB_URI, server_api=ServerApi('1'))
db = client.get_database(DB_NAME)


system_prompts_path = os.path.join(
    os.getcwd(), "src", "prompt_templates", "system_prompts.json")

with open(system_prompts_path, "r") as file:
    system_prompts = json.load(file)


class TaxBot:
    def __init__(self):
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompts["1"]),
            ("human", "Previous message history: {history}"),
            ("human", "User's new question: {input}"),
        ])
        self.llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-4")
        self.chain = self.prompt_template | self.llm | StrOutputParser()

    async def is_tax_related(self, chat_history: MongoDBChatMessageHistory, prompt):
        history_text = "\n".join(
            f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
            for msg in chat_history.messages
        )
        classification_prompt = (
            "Based on the following conversation history, classify the new prompt as 'tax-related' or 'non-tax-related'. "
            "Provide only the classification:\n\n"
            f"Conversation history:\n{history_text}\n\n"
            f"New prompt:\n{prompt}"
        )
        try:
            response = await self.llm.agenerate(
                messages=[[HumanMessage(content=classification_prompt)]]
            )
            classification = response.generations[0][0].message.content.strip().lower()
            classification = classification.strip("'")
            logging.info(f"Classification: {classification}")
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
        # logging.info(f"Current chat history: {chat_history.messages}")

        is_tax_related = await self.is_tax_related(chat_history, prompt)
        logging.info(f"is_tax_related: {is_tax_related}")

        if not is_tax_related:
            return ("I'm sorry, but I can only help with tax-related queries. Please ask a question related to taxes.", [])

        # Add user message to chat history
        await chat_history.aadd_messages([HumanMessage(content=prompt)])

        try:
            # Generate a response using the RunnableSequence
            response = await self.chain.ainvoke({
                "history": chat_history.messages,
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

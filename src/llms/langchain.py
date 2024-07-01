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

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# MongoDB Atlas credentials
db_user = os.getenv("MONGO_DB_USER")
db_password = os.getenv("MONGO_DB_PASSWORD")
db_name = os.getenv("MONGO_DB_NAME")
db_uri = os.getenv("MONGO_DB_URI")

# Create a new client and connect to the server
client = MongoClient(db_uri, server_api=ServerApi('1'))
db = client.get_database(db_name)


class TaxBot:
    def __init__(self):
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant specialized in providing accurate and reliable tax information. You help users understand tax laws, filing procedures, deductions, credits, and other tax-related queries. Always provide clear, concise, and compliant information based on the latest Indian tax regulations."),
            ("human", "Previous message history: {history}"),
            ("human", "User's new question: {input}"),
        ])
        self.llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-4")
        self.chain = self.prompt_template | self.llm | StrOutputParser()

    async def generate(self, session_id, prompt):

        chat_history = MongoDBChatMessageHistory(
            connection_string=db_uri,
            session_id=session_id,
            database_name=db_name,
            collection_name=f"session-{session_id}",
        )
        logging.info(f"Current chat history: {chat_history.messages}")

        chat_history.add_user_message(prompt)

        # Generate a response using the RunnableSequence
        response = self.chain.invoke({
            "history": chat_history.messages,
            "input": prompt
        })
        chat_history.add_ai_message(response)
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

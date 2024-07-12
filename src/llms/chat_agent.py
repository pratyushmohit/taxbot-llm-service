import logging
import os

import dotenv
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AIMessage, HumanMessage
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_openai import ChatOpenAI

from src.llms.toolkit import ToolKit

# Load environment variables from .env file
dotenv_path = os.path.join(os.getcwd(), ".env")
dotenv.load_dotenv(dotenv_path)

# OpenAI Credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# MongoDB Atlas credentials
DB_URI = os.getenv("MONGO_DB_URI")
DB_NAME = os.getenv("MONGO_DB_NAME")

system_prompts_path = os.path.join(
    os.getcwd(), "src", "prompt_templates", "system_prompts.md")

# Read the Markdown file
with open(system_prompts_path, "r") as file:
    system_prompt = file.read()


class ChatAgent:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-3.5-turbo", max_tokens=500)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Previous chat history: {history}"),
            # ("human", "Related documents: {related_documents}"),
            ("human", "User's new question: {input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])
        self.toolkit = [ToolKit.retrieve_from_vector_database,
                        ToolKit.search_with_tavily]
        
        # Construct the OpenAI Tools agent
        self.agent = create_openai_tools_agent(self.llm, self.toolkit, self.prompt)
        
        # Create an agent executor by passing in the agent and tools
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.toolkit, verbose=True)

    async def generate(self, session_id, prompt):

        chat_history = MongoDBChatMessageHistory(
            connection_string=DB_URI,
            session_id=session_id,
            database_name=DB_NAME,
            collection_name=f"session-{session_id}",
        )

        try:
            # Generate a response using the RunnableSequence
            response = await self.agent_executor.ainvoke({
                "history": chat_history.messages,
                "input": prompt
            })

            logging.info(f"Response: {response}")

            # Add user message to chat history
            await chat_history.aadd_messages([HumanMessage(content=prompt)])
            logging.info(f"HumanMessage added to chat history.")
            
            # Add AI message to chat history
            await chat_history.aadd_messages([AIMessage(content=response["output"])])
            logging.info(f"AIMessage added to chat history.")

            # Convert messages to list of dictionaries
            serialized_messages = []
            for msg in response["history"]:
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

            return response["output"], serialized_messages
        
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return ("An error occurred while processing your request.", [])
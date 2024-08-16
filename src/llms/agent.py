import logging
import os

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AIMessage, HumanMessage
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_openai import ChatOpenAI

from src.llms.toolkit import (classify, retrieve_from_vector_database,
                              search_with_tavily)
from src.llms.llm import get_model_initializer
from utils.env_variables import EnvironmentVariables as env

system_prompts_path = os.path.join(
    os.getcwd(), "src", "prompts", "system", "main.md")

# Read the Markdown file
with open(system_prompts_path, "r") as file:
    system_prompt = file.read()


class ChatAgent:
    def __init__(self) -> None:
        initializer = get_model_initializer(
            provider="openai", model_name="gpt-3.5-turbo")
        initializer.initialize_model()
        self.llm = initializer.llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Previous chat history: {history}"),
            ("human", "User's new question: {input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])
        self.toolkit = [classify,
                        retrieve_from_vector_database,
                        search_with_tavily]

        # Construct the OpenAI Tools agent
        self.agent = create_tool_calling_agent(
            llm=self.llm, tools=self.toolkit, prompt=self.prompt)

        # Create an agent executor by passing in the agent and tools
        self.agent_executor = AgentExecutor(
            name="Onnecta Tax Assistant", agent=self.agent, tools=self.toolkit, verbose=True)

    async def generate(self, session_id, prompt):

        chat_history = MongoDBChatMessageHistory(
            connection_string=env.DB_URI,
            session_id=session_id,
            database_name=env.DB_NAME,
            collection_name=session_id,
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

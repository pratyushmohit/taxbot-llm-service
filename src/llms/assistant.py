import logging
import os
from typing import Literal

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import AIMessage, HumanMessage
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from src.llms.llm import get_model_initializer
from src.llms.toolkit import (classify, retrieve_from_vector_database,
                              search_with_tavily)
from utils.env_variables import EnvironmentVariables as env

# @tool
# def get_weather(location: str):
#     """Call to get the current weather."""
#     if location.lower() in ["sf", "san francisco"]:
#         return "It's 60 degrees and foggy."
#     else:
#         return "It's 90 degrees and sunny."


# @tool
# def get_coolest_cities():
#     """Get a list of coolest cities"""
#     return "nyc, sf"

# tools = [get_weather, get_coolest_cities]
# tool_node = ToolNode(tools)

# model_with_tools = ChatOpenAI(api_key=OPENAI_API_KEY,model_name="gpt-3.5-turbo", max_tokens=512).bind_tools(tools)

# def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
#     messages = state["messages"]
#     last_message = messages[-1]
#     if last_message.tool_calls:
#         return "tools"
#     return "__end__"


# def call_model(state: MessagesState):
#     messages = state["messages"]
#     response = model_with_tools.invoke(messages)
#     return {"messages": [response]}


# workflow = StateGraph(MessagesState)

# # Define the two nodes we will cycle between
# workflow.add_node("agent", call_model)
# workflow.add_node("tools", tool_node)

# workflow.add_edge("__start__", "agent")
# workflow.add_conditional_edges(
#     "agent",
#     should_continue,
# )
# workflow.add_edge("tools", "agent")

# app = workflow.compile()

# # example with a single tool call
# for chunk in app.stream(
#     {"messages": [("human", "what's the weather in sf?")]}, stream_mode="values"
# ):
#     chunk["messages"][-1].pretty_print()

# # example with a multiple tool calls in succession

# for chunk in app.stream(
#     {"messages": [("human", "what's the weather in the coolest cities?")]},
#     stream_mode="values",
# ):
#     chunk["messages"][-1].pretty_print()

"""FROM HERE"""
system_prompts_path = os.path.join(
    os.getcwd(), "src", "prompts", "system", "main.md")

# Read the Markdown file
with open(system_prompts_path, "r") as file:
    system_prompt = file.read()


class ChatAssistant:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(api_key=env.OPENAI_API_KEY,
                              model_name="gpt-3.5-turbo", max_tokens=512)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            # ("human", "Previous chat history: {history}"),
            ("human", "User's new question: {input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])
        self.toolkit = [classify,
                        retrieve_from_vector_database,
                        search_with_tavily]
        self.agent = self.llm.bind_tools(self.toolkit)
        self.graph = StateGraph(MessagesState)

    async def build_graph(self):

        def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
            messages = state["messages"]
            last_message = messages[-1]
            if last_message.tool_calls:
                return "tools"
            return "__end__"

        # Define the nodes
        self.graph.add_node("agent", self.agent)
        tool_node = ToolNode(self.toolkit)
        self.graph.add_node("tools", tool_node)

        self.graph.add_edge("__start__", "agent")
        self.graph.add_conditional_edges("agent", should_continue)
        self.graph.add_edge("tools", "agent")
        memory = MemorySaver()
        workflow = self.graph.compile(checkpointer=memory)
        return workflow

    async def generate(self, session_id, prompt):
        try:
            workflow = await self.build_graph()
            # Generate a response using the RunnableSequence
            config = {"configurable": {"thread_id": "thread-1"}}
            response = await workflow.ainvoke({
                # "history": chat_history.messages,
                "input": prompt,
            }, config)

            logging.info(f"Response: {response}")
            # # Add user message to chat history
            # await chat_history.aadd_messages([HumanMessage(content=prompt)])
            # logging.info(f"HumanMessage added to chat history.")

            # # Add AI message to chat history
            # await chat_history.aadd_messages([AIMessage(content=response["output"])])
            # logging.info(f"AIMessage added to chat history.")

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

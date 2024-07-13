from pydantic import BaseModel, Field
from typing import Type, Optional
from langchain_core.tools import BaseTool
from langchain_core.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.tools.tavily_search import TavilySearchResults
import getpass
import os

os.environ["TAVILY_API_KEY"] = getpass.getpass()

# class AddInput(BaseModel):
#     a: int = Field(description="first number")
#     b: int = Field(description="second number")

# class AddTool(BaseTool):
#     name = "add"
#     description = "Adds two numbers together"
#     args_schema: Type[BaseModel] = AddInput
#     return_direct: bool = True

#     def _run(
#         self, a: int, b: int, run_manager: Optional[CallbackManagerForToolRun] = None
#     ) -> str:
#         return a + b


@tool
def add(a: int, b: int) -> int:
    '''Adds two numbers together'''  # this docstring gets used as the description
    return a + b  # the actions our tool performs


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


@tool
def square(a) -> int:
    """Calculates the square of a number."""
    a = int(a)
    return a * a

@tool
def search_api(prompt):
    """Searches the relevant context on the web through Tavily Search API for a given prompt."""
    tool = TavilySearchResults()
    tool.invoke({"query": prompt})


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant specialized in providing accurate and reliable tax information. You help users understand tax laws, filing procedures, deductions, credits, and other tax-related queries. Always provide clear, concise, and compliant information based on the latest Indian tax regulations. Use your tools to answer questions if needed."),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)


toolkit = [add, multiply, square]

# Choose the LLM that will drive the agent
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# setup the toolkit
toolkit = [add, multiply, square, search_api]

# Construct the OpenAI Tools agent
agent = create_openai_tools_agent(llm, toolkit, prompt)

# Create an agent executor by passing in the agent and tools
agent_executor = AgentExecutor(agent=agent, tools=toolkit, verbose=True)

# result = agent_executor.invoke({"input": "Hello"})
# result = agent_executor.invoke({"input": "what is 1 + 1?"})
result = agent_executor.invoke({"input": "what is the current current weather?"})

print(result['output'])

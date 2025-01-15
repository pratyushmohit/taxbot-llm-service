from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
from utils.env_variables import EnvironmentVariables as env


class LLMInitializer(ABC):
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.llm = None

    @abstractmethod
    def initialize_model(self):
        pass


class OpenAIModelInitializer(LLMInitializer):
    def initialize_model(self):
        self.llm = ChatOpenAI(api_key=env.OPENAI_API_KEY,model_name=self.model_name, max_tokens=512)


# Factory method to get the right initializer
def get_model_initializer(provider: str, model_name: str) -> LLMInitializer:
    if provider == 'openai':
        return OpenAIModelInitializer(model_name)
    else:
        raise ValueError(f"Unknown provider: {provider}")
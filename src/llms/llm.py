from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
# from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
# from langchain_ollama import ChatOllama
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


# class MetaModelInitializer(LLMInitializer):
#     def initialize_model(self):
#         # llm_endpoint = HuggingFaceEndpoint(
#         #     repo_id="meta-llama/Meta-Llama-3.1-8B",
#         #     task="text-generation",
#         #     max_new_tokens=512,
#         #     do_sample=False,
#         #     repetition_penalty=1.03,
#         #     huggingfacehub_api_token=env.HUGGINGFACE_API_KEY
#         # )
#         # self.llm = ChatHuggingFace(llm=llm_endpoint)
#         self.llm = ChatOllama(model="llama3.1")

# class AnthropicModelInitializer(LLMInitializer):
#     def initialize_model(self):
#         # Initialize Anthropic models here
#         pass


# Factory method to get the right initializer
def get_model_initializer(provider: str, model_name: str) -> LLMInitializer:
    if provider == 'openai':
        return OpenAIModelInitializer(model_name)
    # elif provider == 'meta':
    #     return MetaModelInitializer(model_name)
    # elif provider == 'anthropic':
    #     return AnthropicModelInitializer(model_name)
    else:
        raise ValueError(f"Unknown provider: {provider}")
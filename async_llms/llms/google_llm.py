import os
from openai import OpenAI, AsyncOpenAI

from .openai_llm import AsyncOpenAILLM

class AsyncGoogleLLM(AsyncOpenAILLM):  # __call__ is inherited from AsyncOpenAILLM
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

    def __init__(self) -> None:
        self.check_api_key()
        self.client = AsyncOpenAI(
            api_key=os.environ.get("GOOGLE_API_KEY", default="EMPTY"),
            base_url=self.BASE_URL,
            timeout=int(os.environ.get("ASYNC_LLM_TIMEOUT", default=600))
        )
        print(f"{self.__class__.__name__} timeout: {self.client.timeout}")

    def check_api_key(self) -> None:
        client = OpenAI(
            api_key=os.environ.get("GOOGLE_API_KEY", default="EMPTY"),
            base_url=self.BASE_URL
        )
        client.models.list()

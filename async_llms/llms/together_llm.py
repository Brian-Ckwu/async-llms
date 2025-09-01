import os
from openai import OpenAI, AsyncOpenAI

from async_llms.llms.openai_llm import AsyncOpenAILLM

class AsyncTogetherLLM(AsyncOpenAILLM):
    def __init__(self) -> None:
        self.check_api_key()
        self.client = AsyncOpenAI(
            api_key=os.environ.get("TOGETHER_API_KEY"),
            base_url="https://api.together.xyz/v1",
            timeout=int(os.environ.get("ASYNC_LLM_TIMEOUT", default=600))
        )
        print(f"{self.__class__.__name__} timeout: {self.client.timeout}")

    def check_api_key(self) -> None:
        client = OpenAI(
            api_key=os.environ.get("TOGETHER_API_KEY"),
            base_url="https://api.together.xyz/v1",
            timeout=int(os.environ.get("ASYNC_LLM_TIMEOUT", default=600))
        )

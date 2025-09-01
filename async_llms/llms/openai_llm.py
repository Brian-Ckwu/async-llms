import os
from openai import OpenAI, AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion

class AsyncOpenAILLM:
    def __init__(self, base_url: str = "") -> None:
        self.check_api_key(base_url)
        self.client = AsyncOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", default="EMPTY"),
            base_url=base_url if base_url else None,
            timeout=int(os.environ.get("ASYNC_LLM_TIMEOUT", default=600))
        )
        print(f"{self.__class__.__name__} timeout: {self.client.timeout}")

    def check_api_key(self, base_url: str = "") -> None:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", default="EMPTY"),
            base_url=base_url if base_url else None
        )
        client.models.list()  # will raise an error if the API key is invalid

    # TODO: add retry logic
    async def __call__(
        self,
        custom_id: str,
        body: dict,
        **kwargs
    ) -> dict:
        response: ChatCompletion = await self.client.chat.completions.create(**body)
        return {
            "id": "TBD",
            "custom_id": custom_id,
            "response": {
                "status_code": 200,  # TODO
                "request_id": "TBD",
                "body": response.model_dump(),
            },
            "error": None  # TODO
        }

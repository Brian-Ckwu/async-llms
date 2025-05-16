import os
from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion

class AsyncOpenAILLM:
    def __init__(self, base_url: str = "") -> None:
        self.client = AsyncOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", default="EMPTY"),
            base_url=base_url if base_url else None
        )

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

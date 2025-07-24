import os
from google import genai
from google.genai import types
from datetime import datetime
import time
from typing import Any, Dict

class AsyncGoogleLLM:
    def __init__(self) -> None:
        if os.getenv("USE_VERTEX_AI") == "True":
            self.client = genai.Client(
                vertexai=True,
                project=os.getenv("GOOGLE_PROJECT"),
                location=os.getenv("GOOGLE_LOCATION")
            )
        else:
            self.client = genai.Client(
                api_key=os.getenv("GOOGLE_API_KEY")
            )

        self.check_api_key()

    def check_api_key(self) -> None:
        response = self.client.models.list(config={"page_size": 5})
        print(response.page)

    def convert_messages_to_contents(self, messages: list[dict]) -> str:
        # NOTE: currently only support a single string as input
        if len(messages) != 1:
            raise ValueError("Currently only support a single string as input")
        if messages[0]["role"] != "user":
            raise ValueError("Currently only support user messages as input")
        if type(messages[0]["content"]) != str:
            raise ValueError("Currently only support string as input")
        return messages[0]["content"]

    def convert_openai_body_to_google_body(self, body: dict) -> dict:
        thinking_config = dict()
        if "extra_body" in body:
            thinking_config = body["extra_body"]["extra_body"]["google"]["thinking_config"]
        return {
            "model": body["model"],
            "contents": self.convert_messages_to_contents(body["messages"]),
            "config": types.GenerateContentConfig(
                temperature=body.get("temperature", None),
                max_output_tokens=body.get("max_completion_tokens", body.get("max_tokens", None)),
                candidate_count=body.get("n", None),
                top_p=body.get("top_p", None),
                response_logprobs=body.get("logprobs", None),
                logprobs=body.get("top_logprobs", None),
                seed=body.get("seed", None),
                thinking_config=types.ThinkingConfig(**thinking_config) if thinking_config else None
            )
        }

    def convert_google_response_to_openai_response(
        self,
        response: types.GenerateContentResponse,
    ) -> dict:
        """
        Convert a google.generativeai.types.GenerateContentResponse (or its
        plain-dict equivalent) into an OpenAI-style chat.completion payload.

        • Any OpenAI fields that Gemini does not supply are set to None.
        • Important Gemini-specific keys are appended verbatim for traceability.
        """
        # ------------------------------------------------------------------ #
        # 0.  Normalise to a plain dict so the rest of the code can be agnostic
        # ------------------------------------------------------------------ #
        response = response.model_dump()

        # ------------------------------------------------------------------ #
        # 1.  Convenience helpers
        # ------------------------------------------------------------------ #
        def _epoch(ts: Any) -> int | None:
            """Return a UTC epoch‐seconds integer (or None)."""
            if isinstance(ts, datetime):
                return int(ts.timestamp())
            if isinstance(ts, (int, float)):
                return int(ts)
            return None

        # ------------------------------------------------------------------ #
        # 2.  Top-level skeleton
        # ------------------------------------------------------------------ #
        openai: Dict[str, Any] = {
            "id": f"chatcmpl-{response.get('response_id', 'unknown')}",
            "object": "chat.completion",
            "created": _epoch(response.get("create_time")) or int(time.time()),
            "model": response.get("model_version"),
            "system_fingerprint": None,   # not provided by Gemini
            "service_tier": None,         # not provided by Gemini
            # choices and usage filled below
        }

        # ------------------------------------------------------------------ #
        # 3.  Choices block
        # ------------------------------------------------------------------ #
        oa_choices = []
        for idx, cand in enumerate(response.get("candidates", [])):
            # --- message text ------------------------------------------------
            parts = cand.get("content", {}).get("parts", [])
            text = "".join(part.get("text", "") for part in parts)

            # --- logprobs ----------------------------------------------------
            logprobs_block = None
            lp_src = cand.get("logprobs_result")
            if lp_src:
                chosen_candidates = lp_src["chosen_candidates"]
                top_candidates = lp_src["top_candidates"]
                assert len(chosen_candidates) == len(top_candidates)
                logprobs_block = {
                    "content": [{
                        "token": chosen["token"],
                        "bytes": list(chosen["token"].encode("utf-8")),
                        "token_id": chosen["token_id"],
                        "logprob": chosen["log_probability"],
                        "top_logprobs": [
                            {
                                "token": candidate.get("token"),
                                "bytes": list(candidate.get("token").encode("utf-8")),
                                "token_id": candidate.get("token_id"),
                                "logprob": candidate.get("log_probability"),
                            }
                            for candidate in top["candidates"]
                        ],
                    } for chosen, top in zip(chosen_candidates, top_candidates)],
                    "refusal": None,
                }

            oa_choices.append({
                "index": cand.get("index", idx),
                "message": {
                    "role": "assistant",
                    "content": text,
                    "function_call": None,
                    "tool_calls": None,
                    "annotations": [],
                    "audio": None,
                    "refusal": None,
                },
                "finish_reason": (
                    cand.get("finish_reason").value.lower()
                    if cand.get("finish_reason") else None
                ),
                "logprobs": logprobs_block,
            })
        openai["choices"] = oa_choices

        # ------------------------------------------------------------------ #
        # 4.  Usage block
        # ------------------------------------------------------------------ #
        usage_src = response.get("usage_metadata", {})
        openai["usage"] = {
            "prompt_tokens": usage_src.get("prompt_token_count"),
            "completion_tokens": usage_src.get("candidates_token_count"),
            "total_tokens": usage_src.get("total_token_count"),
            "prompt_tokens_details": usage_src.get("prompt_tokens_details"),
            "completion_tokens_details": usage_src.get("candidates_tokens_details"),
        }

        # ------------------------------------------------------------------ #
        # 5.  Preserve useful Gemini-specific metadata (optional but handy)
        # ------------------------------------------------------------------ #
        for key in (
            "sdk_http_response",
            "prompt_feedback",
            "automatic_function_calling_history",
            "parsed",
            "usage_metadata",
        ):
            if key in response:
                openai[key] = response[key]

        return openai

    async def __call__(
        self,
        custom_id: str,
        body: dict,
        **kwargs
    ) -> dict:
        body = self.convert_openai_body_to_google_body(body)
        response: types.GenerateContentResponse = await self.client.aio.models.generate_content(**body)
        return {
            "id": "TBD",
            "custom_id": custom_id,
            "response": {
                "status_code": 200,  # TODO
                "request_id": "TBD",
                "body": self.convert_google_response_to_openai_response(response),
            },
            "error": None  # TODO
        }

def get_llm(api_type: str, base_url: str = ""):
    if api_type == "openai":
        from llms.openai_llm import AsyncOpenAILLM
        return AsyncOpenAILLM(base_url=base_url)
    else:
        raise ValueError(f"API type {api_type} not supported")
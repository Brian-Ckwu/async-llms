def get_llm(api_type: str, base_url: str = ""):
    if api_type == "openai":
        from .openai_llm import AsyncOpenAILLM
        return AsyncOpenAILLM(base_url=base_url)
    elif api_type == "google":
        from .google_llm import AsyncGoogleLLM
        return AsyncGoogleLLM()
    else:
        raise ValueError(f"API type {api_type} not supported")
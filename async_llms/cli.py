import asyncio
from pathlib import Path
from argparse import ArgumentParser, Namespace

from .inference import run_inference

def setup_args() -> Namespace:
    parser = ArgumentParser(description="Run asynchronous LLM inference")
    parser.add_argument("--api_type", type=str, choices=["openai", "google", "xai"], default="openai", help="Type of the LLM API")
    parser.add_argument("--base_url", type=str, default="", help="(Optional) The custom base URL used in OpenAI client (e.g., served by vLLM or SGLang)")
    parser.add_argument("--input_jsonl", type=Path, required=True, help="The path to the input jsonl file for async LLM inference.")
    parser.add_argument("--output_jsonl", type=Path, required=True, help="The path to save the inference results.")
    parser.add_argument("--metadata_json", type=Path, default=None, help="The path to the metadata json file storing statistics of LLM API calls (e.g., token usage).")
    parser.add_argument("--num_parallel_tasks", type=int, default=500, help="The number of parallel inference tasks to run.")
    return parser.parse_args()

def main():
    args = setup_args()
    asyncio.run(run_inference(args))

if __name__ == "__main__":
    main()

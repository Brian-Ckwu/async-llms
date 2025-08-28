import json
import asyncio
from pathlib import Path
from tqdm.asyncio import tqdm
from argparse import Namespace
import aiofiles
from typing import Dict, Any

from .llms import get_llm

async def write_to_file(output_jsonl: Path, response: Dict[str, Any]) -> None:
    async with aiofiles.open(output_jsonl, "a") as f:
        await f.write(json.dumps(response) + "\n")

async def llm_inference(
    llm,
    sem: asyncio.Semaphore,
    custom_id: str,
    body: dict,
    output_jsonl: Path,
) -> None:
    async with sem:
        try:
            response = await llm(custom_id, body)
            await write_to_file(output_jsonl, response)
        except Exception as e:
            print(f"Error processing request {custom_id}: {e}")
            # Write error response to file
            error_response = {
                "id": "TBD",
                "custom_id": custom_id,
                "response": {
                    "status_code": 500,  # TODO
                    "request_id": "TBD",
                    "body": {"choices": [{"message": {"content": str(e)}}]},
                },
                "error": str(e)
            }
            await write_to_file(output_jsonl, error_response)

def calc_output_stats(output_jsonl: Path) -> Dict[str, Any]:
    stats = {
        "num_requests": 0,
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
    }
    with open(output_jsonl, "r") as f:
        for line in f:
            data = json.loads(line)
            usage = data["response"]["body"]["usage"]
            stats["num_requests"] += 1
            stats["total_prompt_tokens"] += usage["prompt_tokens"]
            stats["total_completion_tokens"] += usage["completion_tokens"]
    stats.update({
        "avg_prompt_tokens": stats["total_prompt_tokens"] / stats["num_requests"],
        "avg_completion_tokens": stats["total_completion_tokens"] / stats["num_requests"],
    })
    return stats

async def run_inference(args: Namespace) -> None:
    try:
        llm = get_llm(args.api_type, args.base_url)
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        return

    # Clear the output file
    async with aiofiles.open(args.output_jsonl, "w") as f:
        await f.write("")

    sem = asyncio.Semaphore(args.num_parallel_tasks)
    tasks = list()
    with open(args.input_jsonl, "r") as f:
        for line in f:
            data = json.loads(line)
            tasks.append(
                llm_inference(
                    llm=llm,
                    sem=sem,
                    custom_id=data["custom_id"],
                    body=data["body"],
                    output_jsonl=args.output_jsonl,
                )
            )
    for coroutine in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"Running inference with semaphore (max_concurrent={args.num_parallel_tasks})"):
        await coroutine

    if args.metadata_json is not None:
        stats = calc_output_stats(args.output_jsonl)
        with open(args.metadata_json, "w") as f:
            json.dump(stats, f, indent=4)

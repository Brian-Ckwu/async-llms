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
    task_queue: asyncio.Queue,
    progress_event: asyncio.Event,
    output_jsonl: Path,
) -> None:
    while True:
        try:
            custom_id, body = await task_queue.get()
            try:
                response = await llm(custom_id, body)
                await write_to_file(output_jsonl, response)
                progress_event.set()
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
                progress_event.set()
            finally:
                task_queue.task_done()
        except asyncio.CancelledError:
            break

async def run_inference(args: Namespace) -> None:
    try:
        llm = get_llm(args.api_type, args.base_url)
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        return

    # Clear the output file
    async with aiofiles.open(args.output_jsonl, "w") as f:
        await f.write("")

    n_tasks = 0
    task_queue = asyncio.Queue()
    with open(args.input_jsonl, "r") as f:
        for line in f:
            data = json.loads(line)
            task_queue.put_nowait(item=(data["custom_id"], data["body"]))
            n_tasks += 1

    progress_event = asyncio.Event()
    workers = [asyncio.create_task(
        llm_inference(
            llm=llm,
            task_queue=task_queue,
            progress_event=progress_event,
            output_jsonl=args.output_jsonl,
        )
    ) for _ in range(min(args.num_parallel_tasks, n_tasks))]

    completed = 0
    with tqdm(total=n_tasks, desc="Running inference") as pbar:
        while completed < n_tasks:
            await progress_event.wait()
            progress_event.clear()
            completed = n_tasks - task_queue.qsize()
            pbar.n = completed
            pbar.refresh()

    await task_queue.join()

    for worker in workers:
        worker.cancel()
    await asyncio.gather(*workers, return_exceptions=True)

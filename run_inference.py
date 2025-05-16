import json
import asyncio
from pathlib import Path
from tqdm.asyncio import tqdm
from argparse import ArgumentParser, Namespace

from llms import get_llm

def setup_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--api_type", type=str, choices=["openai", "google"], default="openai", help="Type of the LLM API")
    parser.add_argument("--base_url", type=str, default="", help="(Optional) The custom base URL used in OpenAI client (e.g., served by vLLM or SGLang)")
    parser.add_argument("--input_jsonl", type=Path, required=True, help="The path to the input jsonl file for async LLM inference.")
    parser.add_argument("--output_jsonl", type=Path, required=True, help="The path to save the inference results.")
    parser.add_argument("--num_parallel_tasks", type=int, default=500, help="The number of parallel inference tasks to run.")
    return parser.parse_args()

async def llm_inference(
    llm,
    task_queue: asyncio.Queue,
    progress_event: asyncio.Event,
    output_jsonl: Path,
) -> None:
    while True:
        try:
            custom_id, body = await task_queue.get()
            response = await llm(custom_id, body)
            with open(output_jsonl, "a") as f:
                f.write(json.dumps(response) + "\n")
            progress_event.set()
            task_queue.task_done()
        except asyncio.CancelledError:
            break

async def main(args: Namespace) -> None:
    llm = get_llm(args.api_type, args.base_url)
    args.output_jsonl.write_text("")  # clear the output file

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

if __name__ == "__main__":
    args = setup_args()
    asyncio.run(main(args))

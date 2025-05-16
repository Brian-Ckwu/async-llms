# `async-llms`: A Python Library for Asynchronous LLM Calls

`async-llms` is a Python library for making asynchronous LLM calls to accelerate LLM evaluation experiments.

## Installation

You can install the package using pip:

```bash
pip install async-llms
```

## Usage

### Command Line Interface

You can use the package directly from the command line:

```bash
async-llms \
    --api_type "openai" \
    --input_jsonl "path/to/input.jsonl" \
    --output_jsonl "path/to/output.jsonl" \
    --num_parallel_tasks "num_parallel_tasks"
```

### Python API

You can also use the package in your Python code:

```python
from async_llms.inference import run_inference
from pathlib import Path
import asyncio

args = Namespace(
    api_type="openai",
    base_url="",  # Optional custom base URL
    input_jsonl=Path("path/to/input.jsonl"),
    output_jsonl=Path("path/to/output.jsonl"),
    num_parallel_tasks=500
)

asyncio.run(run_inference(args))
```

## Input Format

The input JSONL file should contain one JSON object per line, with each object having the following structure:

```json
{
    "custom_id": "unique_id_for_this_request",
    "body": {
        // Your LLM request parameters here
    }
}
```

## License

MIT License

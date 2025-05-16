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

## Input Format

The input JSONL file format is identical to the one used in OpenAI's Batch API: https://platform.openai.com/docs/guides/batch

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

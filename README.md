# `async-llms`: A Python Library for Asynchronous LLM Calls

`async-llms` is a Python library for making asynchronous LLM calls to accelerate LLM evaluation experiments.

## Installation

You can install the package using pip:

```bash
pip install async-llms
```

## Usage

### Set API Key
Set the API key for the LLM provider you want to use.
```bash
export OPENAI_API_KEY="your_api_key"
export GOOGLE_API_KEY="your_api_key"
```

### (Optional) Set Timeout
You can set the timeout for the LLM calls using the `ASYNC_LLM_TIMEOUT` environment variable.
```bash
export ASYNC_LLM_TIMEOUT=1800  # 1800 seconds per request
```

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

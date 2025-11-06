import re
import json


def extract_filename(prompt: str) -> str:
    """Extract the HTML filename from the prompt text."""
    match = re.search(r"(\w+(?:-\w+)*)\.html", prompt)
    return match.group(0) if match else None


def extract_json_from_text(text):
    code_block_pattern = r"```(?:json)?(.*?)```"
    code_blocks = re.findall(code_block_pattern, text, re.DOTALL)

    if code_blocks:
        for block in code_blocks:
            try:
                return json.loads(block.strip())
            except json.JSONDecodeError:
                continue

    try:
        start_idx = text.find("{")
        end_idx = text.rfind("}")

        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            potential_json = text[start_idx : end_idx + 1]
            return json.loads(potential_json)
    except json.JSONDecodeError:
        pass


def extract_prompt_list(response: str):
    try:
        start = response.find("[")
        end = response.rfind("]")

        if start == -1 or end == -1 or end < start:
            raise ValueError("Brackets not found or malformed in response.")

        list_str = response[start : end + 1]
        parsed = json.loads(list_str)

        if not isinstance(parsed, list) or not all(
            isinstance(item, str) for item in parsed
        ):
            raise ValueError("Extracted content is not a list of strings.")

        return parsed

    except json.JSONDecodeError as e:
        raise ValueError("Failed to decode JSON list from LLM response.") from e

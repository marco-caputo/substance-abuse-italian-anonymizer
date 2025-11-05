import re
import json
import requests


def _extract_clean_json(text: str):
    """
    Extracts and cleans a JSON array or object from a LLM-generated string that may contain
    Markdown code fences, explanations, or other text before/after it.
    Raises ValueError if no valid JSON block is found.

    :param text: The raw text output from the LLM.
    :return: a Python object (list or dict) parsed from the JSON.
    """

    # 1. Remove markdown code fences like ```json ... ``` or ``` ... ```
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = re.sub(r"```", "", cleaned)

    # 2. Extract the first JSON object ({...}) or array ([...])
    json_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
    if not json_match:
        print("No JSON object or array found in the text. Full text:\ntext")
        return []

    json_str = json_match.group(1).strip()

    # 3. Attempt to parse JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        # 4. Raise a clearer error if JSON is malformed
        print(f"Invalid JSON structure: {e}\nExtracted string:\n{json_str}")
        return []

def send_prompt(prompt: str, method: str ='gpt4-web-api') -> list:
    resp = requests.get("http://127.0.0.1:5500/", params={"text": prompt})
    return _extract_clean_json(resp.text)
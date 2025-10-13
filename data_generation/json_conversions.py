import json
import re


def extract_clean_json(text: str):
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
        raise ValueError("No JSON object or array found in the text.")

    json_str = json_match.group(1).strip()

    # 3. Attempt to parse JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        # 4. Raise a clearer error if JSON is malformed
        raise ValueError(f"Invalid JSON structure: {e}\nExtracted string:\n{json_str}")

# Convert to spaCy training format
def to_spacy_format(example):
    """
    Converts a single json example with "text" and "entities" fields into spaCy's training format.
    Each of the entities of the input example is a dict with "text" and "label" keys.

    :param example: A dict with "text" and "entities" keys.
    :return: A tuple (text, {"entities": [(start, end, label), ...]})
    """
    text = example["text"]
    entities = []
    for ent in example["entities"]:
        start = text.find(ent["text"])
        if start == -1:
            continue  # skip if substring not found
        end = start + len(ent["text"])
        entities.append((start, end, ent["label"]))
    return (text, {"entities": entities})
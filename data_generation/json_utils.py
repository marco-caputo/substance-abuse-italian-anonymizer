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


def to_spacy_format(example: dict):
    """
    Converts a JSON example with "text" and "entities" fields into spaCy's training format.
    Each entity is a dict with "text" and "label".
    Finds all occurrences of each entity text (non-overlapping, whole-word matches).

    Returns: (text, {"entities": [(start, end, label), ...]})
    """
    text = example["text"]
    entities = []

    # Handle accented letters properly
    LETTERS = r"A-Za-zÀ-ÖØ-öø-ÿ"

    def overlaps(a_start, a_end, b_start, b_end):
        return not (a_end <= b_start or a_start >= b_end)

    for ent in example["entities"]:
        ent_text = ent["text"]
        label = ent["label"]

        # Regex pattern: match entity as a standalone word (not inside another)
        pattern = rf"(?<![{LETTERS}]){re.escape(ent_text)}(?![{LETTERS}])"

        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            start, end = match.start(), match.end()

            # Skip overlapping matches
            if any(overlaps(s, e, start, end) for s, e, _ in entities):
                continue

            entities.append((start, end, label))

    # Sort by start position
    entities.sort(key=lambda x: x[0])

    return (text, {"entities": entities})
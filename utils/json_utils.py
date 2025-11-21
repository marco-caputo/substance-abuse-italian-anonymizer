import json
import re
import os

def to_spacy_format(examples: list[dict]):
    """
    Converts a list of JSON examples with "text" and "entities" fields into spaCy's training format.
    Each entity is a dict with "text" and "label".
    Finds all occurrences of each entity text (non-overlapping, whole-word matches).

    Returns: [(text, {"entities": [(start, end, label), ...]}), ...]
    """
    spacy_data = []

    for example in examples:
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
        spacy_data.append((text, {"entities": entities}))

    return spacy_data


def to_readable_format(spacy_examples: list[tuple]) -> list[dict]:
    """
    Converts a list of spaCy training examples back into JSON format with explicit "text" and "entities".
    Each entity is a dict with "text" and "label".
    """
    readable_data = []

    for spacy_example in spacy_examples:
        text, annotations = spacy_example
        entities = []

        for start, end, label in annotations["entities"]:
            ent_text = text[start:end]
            entities.append({"text": ent_text, "label": label})

        readable_data.append({"text": text, "entities": entities})

    return readable_data


def append_json_data(f_name:str, data: list[dict]) -> str:
    """
    Saves sample data to a JSON file. If the file already exists, appends the new data to the existing data.
    :param f_name: complete path and file name of the JSON file
    :param data: list of sample data to save
    :return: the path to the saved file
    """

    # If file exists, load existing data
    if os.path.exists(f_name):
        with open(f_name, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Append new samples
    existing_data.extend(data)

    # Save updated data back to the file
    with open(f_name, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    return f_name


def read_json_file(file_path: str):
    """
    Reads a JSON file and returns its content.
    :param file_path: Path to the JSON file.
    :return: Parsed JSON content.
    """
    with open(file_path, 'r', encoding="utf-8-sig") as file:
        return json.load(file)


def save_json_file(file_path: str, data):
    """
    Saves data to a JSON file.
    :param file_path: Path to the JSON file.
    :param data: Data to be saved.
    """
    with open(file_path, 'w', encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
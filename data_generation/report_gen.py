import json
import os
import re
import requests

from json_conversions import extract_clean_json, to_spacy_format
from gen_config import SYSTEM_PROMPT, ENTITIES, N_PER_OUTPUT, SEED_SAMPLES

def save_spacy_data(filename:str, spacy_data):
    # Build new filename
    match = re.search(r"seed_(.+)\.json", filename)
    if not match:
        raise ValueError(f"Filename '{filename}' does not match pattern 'seed_XXX.json'")
    new_filename = f"synthetic_samples/synthetic_{match.group(1)}.json"

    # If file exists, load existing data
    if os.path.exists(new_filename):
        with open(new_filename, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Append new samples
    existing_data.extend(spacy_data)

    # Save updated data back to the file
    with open(new_filename, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    return new_filename


if __name__ == "__main__":
    for samples_file in SEED_SAMPLES:
        with open(f'seed_samples/{samples_file['filename']}', 'r') as file:
            seed_examples = json.load(file)

        # Build the few-shot prompt
        examples_text = json.dumps(seed_examples, indent=2)

        prompt = f"""
        {SYSTEM_PROMPT}\n
        For instance, this is what you should answer when receiving a request for {len(seed_examples)} samples:\n
        {examples_text}\n
        Now generate {N_PER_OUTPUT} new {samples_file['description']} samples about patients in substance abuse treatment. 
        Ensure each example resembles a realistic {samples_file['description']} in italian as those provided above,
        but don't be afraid to vary the style, content and length of the reports.
        Possible entities that can be included are:\n 
        {"\n".join([f"- {e["label"]}: {e["desc"]}" for e in ENTITIES])}\n
        {samples_file.get('additional_instructions', '')}
        """

        for i in range(samples_file['n_outputs']):
            # Generate synthetic examples
            resp = requests.get("http://127.0.0.1:5500/", params={"text": prompt})
            data = extract_clean_json(resp.text)
            spacy_data = [to_spacy_format(ex) for ex in data]  # handle "examples" wrapper or list
            filename = save_spacy_data(samples_file['filename'], spacy_data)
            print(f"Generation {i+1}/{samples_file['n_outputs']} from {samples_file['filename']} - "
                  f"{len(spacy_data)} synthetic examples saved in {filename}")
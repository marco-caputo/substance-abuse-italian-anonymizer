import json
from json_conversions import extract_clean_json, to_spacy_format
from gen_config import SYSTEM_PROMPT, ENTITIES, N_PER_OUTPUT

import requests

with open('seed_examples.json', 'r') as file:
    seed_examples = json.load(file)

# Build the few-shot prompt
examples_text = json.dumps(seed_examples, indent=2)


prompt = f"""
{SYSTEM_PROMPT}\n
For instance, this is what you should answer when receiving a request for {len(seed_examples)} samples:\n
{examples_text}\n
Now generate {N_PER_OUTPUT} new therapy report samples about patients in substance abuse treatment. 
Ensure each example resembles a realistic clinical note or therapy report in italian as those provided above,
and don't be afraid to vary the style, content and length of the reports.
Possible entities to be included are {", ".join(ENTITIES)}.
"""

# Generate synthetic examples
resp = requests.get("http://127.0.0.1:5500/", params={"text": prompt})
data = extract_clean_json(resp.text)

spacy_data = [to_spacy_format(ex) for ex in data]  # handle "examples" wrapper or list

# Save to JSON file
with open("synthetic_ner_data.json", "w", encoding="utf-8") as f:
    json.dump(spacy_data, f, ensure_ascii=False, indent=2)

print(f"Generated {len(spacy_data)} synthetic examples and saved to synthetic_ner_data.json")

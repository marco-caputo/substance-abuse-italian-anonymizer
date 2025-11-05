import json
import re

import random
from faker import Faker

from data_generation.mistakes_cleaner import clean_common_mistakes
from prompt_sender import send_prompt

faker = Faker('it_IT')

from utils.json_utils import read_json_file, append_json_data
from config import SYSTEM_PROMPT, ENTITIES, SEED_SAMPLES, PROMPT_REPORTS_1, PROMPT_REPORTS_2
from mistakes_cleaner import replace_common_names, clean_wrong_per

def save_and_print(data: list[dict], samples_files: dict, iteration: int):
    filename = append_json_data(f"synthetic_{samples_files['filename']}_train", data)
    print(f"Generation {iteration + 1}/{samples_files['n_outputs']} from {samples_files['filename']} - "
          f"{len(data)} synthetic examples saved in {filename}")

def generate_examples(p: str, samples_files: dict, iteration: int):
    data = send_prompt(p)
    data = [clean_common_mistakes(ex) for ex in data]
    data = [replace_common_names(ex) for ex in data]
    save_and_print(data, samples_files, iteration)

def clean_street_with_number(address: str) -> str:
    """Keeps the street name and the first number, cuts off everything that comes after."""
    match = re.match(r'^(.*?\d+)', address)
    return match.group(1).strip() if match else address.strip()

def generate_report_prompt_data():
    """Generates random data for report one-shot prompt generation."""
    intro = random.choice(read_json_file(f"seed_samples/seed_report_info.json")["intros"])
    outro = random.choice(["", random.choice(read_json_file(f"seed_samples/seed_report_info.json")["outros"])])
    docname = random.choice(read_json_file(f"seed_samples/seed_report_info.json")["docname"])
    name = re.sub(r'^(?:[A-Za-z]+\.)+\s*', '', faker.name())  # Remove titles
    name = re.sub(r'-.*', '', name)  # Remove anything after hyphen
    chapters = ', '.join(
        random.sample(read_json_file(f"seed_samples/seed_report_info.json")["chapters"], k=random.randint(2, 6)))
    where = f"a street named {clean_street_with_number(faker.street_address())}, municipality of {faker.city()}"
    return intro, outro, docname, name, where, chapters

def generate_examples_report(samples_files: dict, iteration: int):
    starting_prompt = PROMPT_REPORTS_1(generate_report_prompt_data())
    json_text = send_prompt(starting_prompt)["text"]
    json_text = replace_common_names(json_text)
    json_entities = send_prompt(PROMPT_REPORTS_2(json_text))
    example = json.loads(json.dumps({
        "text": json_text,
        "entities": json_entities
    }))

    example = clean_wrong_per(example)
    save_and_print([example], samples_files, iteration)

if __name__ == "__main__":
    for samples_file in SEED_SAMPLES[2:-1]:  # Exclude the last one (diaries)

        if samples_file['filename'] == "reports":
            for i in range(samples_file['n_outputs']):
                error = True
                while error:
                    try:
                        generate_examples_report(samples_file, i)
                        error = False
                    except Exception as e:
                        print(f"Error during report generation: {e} \n Retrying...")
                continue

        # Build the few-shot prompt
        seed_examples = read_json_file(f"seed_samples/train/seed_{samples_file['filename']}_train.json")
        examples_text = json.dumps(seed_examples, indent=2)

        # Generate train data
        for i in range(samples_file['n_outputs']):
            # Select a random subset of examples
            current_examples_text = json.dumps(
                random.sample(seed_examples, min(len(seed_examples), samples_file['n_examples_per_prompt'])), indent=2)

            prompt = f"""
                    {SYSTEM_PROMPT}\n
                    For instance, this is {("a small initial excerpt of " if samples_file['filename'] == "reports" else "")}
                    what you should answer when receiving a request for {len(seed_examples)} samples:\n
                    {current_examples_text}\n
                    Now generate {samples_file['n_per_output']} new {samples_file['description']} samples about patients 
                    in substance abuse treatment. 
                    Ensure each example resembles a realistic {samples_file['description']} in Italian as those provided above,
                    but don't be afraid to vary the style, content and length of the reports.
                    Possible entities that can be included are:\n 
                    {"\n".join([f"- {e["label"]}: {e["desc"]}" for e in ENTITIES])}\n
                    {samples_file.get('additional_instructions', '')}
                    """

            generate_examples(prompt, samples_file, i)
import sys
from pathlib import Path
import json
import pandas as pd
from faker import Faker

# Ensures project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from prompts import get_diaries_translation_prompt, get_diaries_ner_prompt, get_staff_diaries_prompt, \
    get_report_label_prompt, get_report_text_prompt
from mistakes_cleaner import clean_common_mistakes, replace_common_names, change_some_entities_to_lowercase
from prompt_sender import send_prompt
from utils import read_json_file, append_json_data
from data_generation.config import SEED_SAMPLES, SEED_PATH_DIARIES, TRAIN_TEST_SPLIT_DIARIES

faker = Faker('it_IT')
N_PER_OUTPUT = SEED_SAMPLES[-1]['n_examples_per_prompt']


def extract_chunks(dataframe):
    """
    Extracts chunks of the first column from the dataframe, each chunk containing SEED_SAMPLES['n_outputs'] rows.
    Returns a list of lists, where each inner list is a chunk of rows.
    :param dataframe: pandas DataFrame with at least one column.
    :return: List of chunks of rows from the dataset, all max length of SEED_SAMPLES['n_outputs'].
    """
    chunks = []
    for start in range(0, len(dataframe), N_PER_OUTPUT):
        first_col_chunk = dataframe.iloc[start:start + N_PER_OUTPUT, 0]
        chunk_list = list(first_col_chunk)
        chunks.append(chunk_list)
    return chunks

def take_diaries_test_portion():
    """Splits the last generated diaries synthetic data into train and test sets."""
    train_examples = read_json_file(f"synthetic_samples/train/synthetic_{SEED_SAMPLES[-1]['filename']}_train.json")
    index_split = int(len(train_examples) * TRAIN_TEST_SPLIT_DIARIES)
    test_examples = train_examples[index_split:]
    train_examples = train_examples[:index_split]

    file_name = f"synthetic_samples/train/synthetic_{SEED_SAMPLES[-1]['filename']}_train.json"
    append_json_data(file_name, train_examples, overwrite=True)
    print(f"Saved {len(train_examples)} train examples in {file_name}")

    file_name = f"synthetic_samples/test/synthetic_{SEED_SAMPLES[-1]['filename']}_test.json"
    append_json_data(file_name, test_examples)
    print(f"Saved {len(test_examples)} test examples to {file_name}")

def generate_diaries(chunk: list[str], iteration: int):
    """Generates, cleans and saves diaries examples in two steps: first translating, then labeling entities."""
    chunk = send_prompt(get_diaries_translation_prompt(chunk))
    if len(chunk) != SEED_SAMPLES[-1]['n_examples_per_prompt']:
        raise Exception(f"Number of examples per prompt ({len(chunk)}) does not match")
    generate_examples(get_diaries_ner_prompt(chunk), SEED_SAMPLES[-1], iteration)

def save_and_print(data: list[dict], samples_files: dict, iteration: int, train_test: str = "train"):
    """Cleans, saves and prints information about generated data."""
    if len(data) != samples_files['n_examples_per_prompt']:
        raise Exception(f"Number of examples per prompt ({len(data)}) does not match")
    data = [clean_common_mistakes(ex) for ex in data]
    data = [replace_common_names(ex) for ex in data]
    data = [change_some_entities_to_lowercase(ex) for ex in data]
    filename = append_json_data(f"synthetic_samples/{train_test}/synthetic_{samples_files['filename']}_{train_test}.json", data)
    print(f"Generation {iteration + 1}/{samples_files['n_outputs'][train_test]} from {samples_files['filename']} - "
          f"{len(data)} synthetic examples saved in {filename}")

def generate_examples(p: str, samples_files: dict, iteration: int, train_test: str = "train"):
    """Generates examples using the provided prompt, cleans and saves them."""
    data = send_prompt(p)
    save_and_print(data, samples_files, iteration, train_test)

def generate_examples_report(samples_files: dict, iteration: int, train_test: str):
    """Generates, cleans and saves report examples in two steps: first generating the text, then labeling entities."""
    starting_prompt = get_report_text_prompt(train_test)
    json_text = send_prompt(starting_prompt)["text"]
    json_text = replace_common_names(json_text)
    second_prompt = get_report_label_prompt(json_text)
    json_entities = send_prompt(second_prompt)
    example = json.loads(json.dumps({
        "text": json_text,
        "entities": json_entities
    }))

    save_and_print([example], samples_files, iteration, train_test)

def main():
    # Prepare diaries seed data
    data = pd.read_csv(SEED_PATH_DIARIES)
    diaries_chunks = extract_chunks(data)

    for samples_file in SEED_SAMPLES[:-1]: # Temporarily exclude diaries_it
        for train_test in (["train", "test"] if samples_file['filename'] != "diaries_it" else ["train"]):
            for i in range(samples_file['n_outputs'][train_test]):
                error = True
                while error:
                    try:
                        if samples_file['filename'] == "reports": generate_examples_report(samples_file, i, train_test)
                        if samples_file['filename'] == "diaries_it": generate_diaries(diaries_chunks[i], i)
                        else:
                            generate_examples(get_staff_diaries_prompt(samples_file, train_test),
                                              samples_file, i, train_test)

                        error = False
                    except Exception as e:
                        print(f"Error during report generation: {e} \n Retrying...")

        if samples_file['filename'] == "diaries_it": take_diaries_test_portion()


if __name__ == "__main__":
    main()
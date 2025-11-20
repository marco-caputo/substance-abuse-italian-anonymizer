import json

import pandas as pd
from config import ENTITIES_NER, SEED_SAMPLES, SYSTEM_PROMPT_DIARIES, SEED_PATH_DIARIES, TRAIN_TEST_SPLIT_DIARIES
from report_gen import generate_examples

N_PER_OUTPUT = SEED_SAMPLES[-1]['n_per_output']


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

def build_prompts(chunks):
    """
    Builds prompts for each chunk of diary entries.
    :param chunks: List of chunks of diary entries.
    :return: List of prompts.
    """
    prompts = []
    filtered_entities = [e for e in ENTITIES_NER if e['label'] not in {'PATIENT'}]
    for i, chunk in enumerate(chunks):
        prompts.append(
            f"""
                {SYSTEM_PROMPT_DIARIES}
                Here are the {N_PER_OUTPUT} diary entries that you should modify by inserting named entities:
                \n\n- {"\n\n- ".join(chunk)}\n

                Possible entities that can be included are:\n 
                {"\n".join([f"- {e["label"]}: {e["desc"]}" for e in filtered_entities])}
                Ensure each example resembles a realistic {SEED_SAMPLES[-1]['description']}\n
                {SEED_SAMPLES[-1]["additional_instructions"]}
            """
        )
    return prompts

def take_test_portion():
    with open(f"synthetic_samples/synthetic_{SEED_SAMPLES[-1]['filename']}_train.json", 'r', encoding="utf-8-sig") as file:
        train_examples = json.load(file)

    index_split = int(len(train_examples) * TRAIN_TEST_SPLIT_DIARIES)
    test_examples = train_examples[index_split:]
    train_examples = train_examples[:index_split]

    with open(f"synthetic_samples/synthetic_{SEED_SAMPLES[-1]['filename']}_train.json", 'w', encoding="utf-8-sig") as file:
        json.dump(train_examples, file, ensure_ascii=False, indent=2)
        print(f"Saved{len(train_examples)} train examples in seed_samples/train/seed_{SEED_SAMPLES[-1]['filename']}_train.json")

    with open(f"seed_samples/test/seed_{SEED_SAMPLES[-1]['filename']}_test.json", 'w', encoding="utf-8-sig") as file:
        json.dump(test_examples, file, ensure_ascii=False, indent=2)
        print(f"Saved {len(test_examples)} test examples to seed_samples/test/seed_{SEED_SAMPLES[-1]['filename']}_test.json")

def main():
    data = pd.read_csv(SEED_PATH_DIARIES)
    chunks = extract_chunks(data)
    prompts = build_prompts(chunks)[65:]

    for i, prompt in enumerate(prompts, 66):
        generate_examples(prompt, SEED_SAMPLES[-1], i)

    take_test_portion()

if __name__ == "__main__":
    main()
import pandas as pd
from diaries_config import SEED_PATH, SYSTEM_PROMPT, SEED_SAMPLE
from config import ENTITIES, SEED_SAMPLES
from report_gen import send_prompt


def extract_chunks(dataframe):
    """
    Extracts chunks of the first column from the dataframe, each chunk containing SEED_SAMPLES['n_outputs'] rows.
    Returns a list of lists, where each inner list is a chunk of rows.
    :param dataframe: pandas DataFrame with at least one column.
    :return: List of chunks of rows from the dataset, all max length of SEED_SAMPLES['n_outputs'].
    """
    chunks = []
    for start in range(0, len(dataframe), SEED_SAMPLES['n_outputs']):
        first_col_chunk = dataframe.iloc[start:start + SEED_SAMPLES['n_outputs'], 0]
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
    filtered_entities = [e for e in ENTITIES if e['label'] not in {'PATIENT'}]
    for i, chunk in enumerate(chunks):
        prompts.append(
            f"""
                {SYSTEM_PROMPT}
                Here are the diary entries that you should modify by inserting named entities:
                {"\n".join(chunk)}\n

                Possible entities that can be included are:\n 
                {"\n".join([f"- {e["label"]}: {e["desc"]}" for e in filtered_entities])}
                Ensure each example resembles a realistic {SEED_SAMPLE['description']}\n
                {SEED_SAMPLE["additional_instructions"]}
            """
        )
    return prompts

def main():
    data = pd.read_csv(SEED_PATH)
    chunks = extract_chunks(data)
    prompts = build_prompts(chunks)
    first_prompt = prompts[0]
    first_prompt = first_prompt
    # print first prompt, remove newlines for better readability
    send_prompt(prompts[0], SEED_SAMPLES[2])
    #print(prompts[0])



if __name__ == "__main__":
    main()
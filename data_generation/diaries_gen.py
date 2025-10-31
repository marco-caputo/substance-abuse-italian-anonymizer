import pandas as pd
from diaries_config import SEED_PATH, NUMBER_OF_ROWS, SYSTEM_PROMPT, SEED_SAMPLE
from config import ENTITIES


def extract_chunks(dataframe):
    """
    Extracts chunks of the first column from the dataframe, each chunk containing NUMBER_OF_ROWS rows.
    Returns a list of lists, where each inner list is a chunk of rows.
    :param dataframe: pandas DataFrame with at least one column.
    :return: List of chunks of rows from the dataset, all max length of NUMBER_OF_ROWS.
    """
    chunks = []
    for start in range(0, len(dataframe), NUMBER_OF_ROWS):
        first_col_chunk = dataframe.iloc[start:start + NUMBER_OF_ROWS, 0]  # Series
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
    for i, chunk in enumerate(chunks):
        prompts.append(
            f"""
                {SYSTEM_PROMPT}
                Here are the diary entries that you should modify by inserting named entities:
                {"\n".join(chunk)}\n

                Possible entities that can be included are:\n 
                {"\n".join([f"- {e["label"]}: {e["desc"]}" for e in ENTITIES])}
                Ensure each example resembles a realistic {SEED_SAMPLE['description']}\n
                {SEED_SAMPLE["additional_instructions"]}
            """
        )
    return prompts

def main():
    data = pd.read_csv(SEED_PATH)
    chunks = extract_chunks(data)
    prompts = build_prompts(chunks)
    # print first prompt, remove newlines for better readability
    print(prompts[0])



if __name__ == "__main__":
    main()
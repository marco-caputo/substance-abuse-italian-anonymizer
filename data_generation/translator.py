import pandas as pd
from deepl import Translator
import argparse
from typing import Tuple

"""
CLI tool to translate a specified column from a CSV using the DeepL API.
Reads an input CSV, translates the values from a named column, and writes
the translations to an output CSV.

Usage (example):
    python translate.py -k "DEEPL_KEY" -i input.csv -o output.csv -t IT -c description
"""

def get_args() -> Tuple[str, str, str, str, str]:
    parser = argparse.ArgumentParser(description="Translate text using DeepL API")
    parser.add_argument("--api_key", "-k", required=True, help="DeepL API key")
    parser.add_argument("--input_file", "-i", required=True, help="Path to input file (CSV)")
    parser.add_argument("--output_file", "-o", required=True, help="Path to output file")
    parser.add_argument("--target_lang", "-t", required=True, help="Target language code")
    parser.add_argument("--column", "-c", required=True, help="Column name to translate")
    args = parser.parse_args()
    return args.api_key, args.input_file, args.output_file, args.target_lang, args.column


def translate_texts(texts: list[str], translator: Translator, target_lang: str) -> list[str]:
    translated_texts = []
    for idx, text in enumerate(texts):
        if text == "":
            translated_texts.append("")
            continue
        try:
            result = translator.translate_text(str(text), target_lang=target_lang)
            translated_texts.append(result.text)
        except Exception as e:
            print(f"Warning: error translating {idx}: {e}")
            translated_texts.append("")
    return translated_texts


def main():
    api_key, input_file, output_file, target_lang, column_to_translate = get_args()
    translator = Translator(api_key)

    df = pd.read_csv(input_file)
    if column_to_translate not in df.columns:
        raise ValueError(f"Column `{column_to_translate}` not present in `{input_file}`")

    translated_texts = translate_texts(df[column_to_translate].tolist(), translator, target_lang)
    translated_df = pd.DataFrame(translated_texts)
    translated_df.to_csv(output_file, index=False)


if __name__ == "__main__":
    main()

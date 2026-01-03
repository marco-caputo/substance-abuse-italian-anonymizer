#!/usr/bin/env python3

import os
import warnings
import argparse
import sys
import json
from typing import Iterable

import spacy
from spacy import Language

from config import DEFAULT_NER_MODEL, DEFAULT_ENTITIES, DEFAULT_EXTRA_PER_MATCHING, PERSONAL_DATA_FORMAT
from rules.rules import apply_rules
from utils.anonymization_utils import anonymize_doc, save_anonymized_text, read_file, save_many_texts
from GUI.GUI import main as gui_main

warnings.filterwarnings("ignore", message=r".*\[W095\].*")

# ----------------------------
#   Anonymization function
# ----------------------------
def anonymize(text: str,
              nlp:Language = None,
              entities:Iterable[str]=None,
              per_matching:bool=None,
              personal_data:dict[str, str]=None) -> str:
    """
    Anonymizes the input text by replacing entities with placeholders only for the specified entity types,
    or the default ones if none are specified.

    :param text: Input text to anonymize.
    :param nlp: pre-loaded spaCy Language model. If None, loads the default
    :param entities: List of entity types to anonymize.
    :param per_matching: Whether to anonymize PER and PATIENT entities in combination with dictionaries or not.
    :param personal_data: Dictionary of specific personal data to anonymize.
    """
    if nlp is None: nlp = spacy.load(DEFAULT_NER_MODEL)
    if entities is None: entities = DEFAULT_ENTITIES
    if per_matching is None: per_matching = DEFAULT_EXTRA_PER_MATCHING

    return anonymize_doc(apply_rules(nlp(text), per_matching, personal_data), entities)

def get_full_labeller(path: str = DEFAULT_NER_MODEL, per_matching:bool=DEFAULT_EXTRA_PER_MATCHING):
    """Returns a full anonymization function using the specified spaCy model path."""
    nlp = spacy.load(path)
    return lambda text: apply_rules(nlp(text), per_matching)

# ----------------------------
#   CLI logic
# ----------------------------

def main():
    parser = argparse.ArgumentParser(description="Anonymize text based on spaCy NER and additional rules.")

    # Command options
    parser.add_argument("--text", type=str, help="Text to anonymize.")
    parser.add_argument("--input-file", type=str, help="Path to a file containing text to anonymize. In case of a json, it can also contain a dictionary of personal data.")
    parser.add_argument("--output-path", type=str, help="Path to save anonymized text. If omitted, prints to stdout.")
    parser.add_argument("--entities", type=str, nargs="+", help="List of entity types to anonymize.")
    parser.add_argument("--per-matching", action="store_true", help="Enable extra matching for PER and PATIENT entities using dictionaries.")
    parser.add_argument("--personal-data", type=str, help=f"Path to json dictionary of specific personal data to anonymize. Provided dictionary should have the following fields: {list(PERSONAL_DATA_FORMAT.keys())}.")
    parser.add_argument("--gui", action="store_true", help="Launch the graphical user interface.")

    args = parser.parse_args()

    # -----------------------------------
    # GUI MODE
    # -----------------------------------
    if args.gui:
        gui_main()
        return

    # -----------------------------------
    # CLI MODE
    # -----------------------------------
    #  Retrieve input text
    texts = None
    entities = None
    personal_data = None

    if args.text:
        texts = [args.text]
    elif args.input_file:
        if not os.path.isfile(args.input_file):
            print(f"Error: Input file '{args.input_file}' does not exist.", file=sys.stderr)
            sys.exit(1)
        try:
            texts, personal_data  = read_file(args.input_file)
        except Exception as e:
            print(f"Error reading file '{args.input_file}': {e}", file=sys.stderr)
            sys.exit(1)
    else: # fallback: read from stdin
        if not sys.stdin.isatty():
            texts = [sys.stdin.read().strip()]

    if not texts:
        print("Error: No text provided. Use --text, --input-file, or provide text via stdin.", file=sys.stderr)
        sys.exit(1)

    if args.entities:
        entities = list(args.entities)

    if args.personal_data:
        try:
            with open(args.personal_data, "r", encoding="utf-8") as f:
                personal_data = json.load(f)
        except Exception as e:
            print(f"Error reading personal data file '{args.personal_data}': {e}", file=sys.stderr)
            sys.exit(1)

    # Load spaCy model
    try:
        nlp = spacy.load(DEFAULT_NER_MODEL)
    except Exception as e:
        print(f"Error loading spaCy model '{args.model}': {e}", file=sys.stderr)
        sys.exit(1)

    # Anonymize
    anonymized = [anonymize(text, nlp=nlp, entities=entities, per_matching=args.per_matching, personal_data=personal_data)
                    for text in texts]

    # Output result
    if args.output_path:
        if not os.path.isdir(args.output_path):
            try:
                out_path = save_anonymized_text('\n\n'.join(anonymized), output_path=args.output_path)
            except Exception as e:
                print(f"Error writing to '{args.output_path}': {e}", file=sys.stderr)
                sys.exit(1)
        else:
            try:
                out_path = save_many_texts(anonymized, output_dir=args.output_path, original_filename=args.input_file)
            except Exception as e:
                print(f"Error writing to directory '{args.output_path}': {e}", file=sys.stderr)
                sys.exit(1)
        print(f"Anonymized text saved to '{out_path}'.")
    elif args.input_file:
        out_path = save_many_texts(anonymized, output_dir=os.path.dirname(args.input_file), original_filename=args.input_file)
        print(f"Anonymized text saved to '{out_path}'.")
    else:
        print(anonymized)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3

import os
import warnings
import argparse
import sys
from typing import Iterable

import spacy
from spacy import Language

from config import DEFAULT_NER_MODEL, DEFAULT_ENTITIES
from rules.rules import apply_rules
from utils.anonymization_utils import anonymize_doc, save_anonymized_text
from GUI.GUI import main as gui_main

warnings.filterwarnings("ignore", message=r".*\[W095\].*")

# ----------------------------
#   Anonymization function
# ----------------------------
def anonymize(text: str, nlp:Language = None, entities:Iterable[str]=None) -> str:
    """
    Anonymizes the input text by replacing entities with placeholders only for the specified entity types,
    or the default ones if none are specified.

    :param text: Input text to anonymize.
    :param nlp: pre-loaded spaCy Language model. If None, loads the default
    :param entities: List of entity types to anonymize.
    """
    if nlp is None: nlp = spacy.load(DEFAULT_NER_MODEL)
    if entities is None: entities = DEFAULT_ENTITIES
    return anonymize_doc(apply_rules(nlp(text)), entities)

# ----------------------------
#   CLI logic
# ----------------------------

def main():
    parser = argparse.ArgumentParser(description="Anonymize text based on spaCy NER and additional rules.")

    # Command options
    parser.add_argument("--text", type=str, help="Text to anonymize.")
    parser.add_argument("--input-file", type=str, help="Path to a file containing text to anonymize.")
    parser.add_argument("--output-file", type=str, help="Path to save anonymized text. If omitted, prints to stdout.")
    parser.add_argument("--entities", type=str, nargs="+", help="List of entity types to anonymize.")
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
    text = None
    entities = None

    if args.text:
        text = args.text
    elif args.input_file:
        if not os.path.isfile(args.input_file):
            print(f"Error: Input file '{args.input_file}' does not exist.", file=sys.stderr)
            sys.exit(1)
        try:
            with open(args.input_file, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file '{args.input_file}': {e}", file=sys.stderr)
            sys.exit(1)
    else: # fallback: read from stdin
        if not sys.stdin.isatty():
            text = sys.stdin.read().strip()

    if not text:
        print("Error: No text provided. Use --text, --input-file, or provide text via stdin.", file=sys.stderr)
        sys.exit(1)

    if args.entities:
        entities = list(args.entities)

    # Load spaCy model
    try:
        nlp = spacy.load(DEFAULT_NER_MODEL)
    except Exception as e:
        print(f"Error loading spaCy model '{args.model}': {e}", file=sys.stderr)
        sys.exit(1)

    # Anonymize
    anonymized = anonymize(text, nlp=nlp, entities=entities)

    # Output result
    if args.output_file:
        try:
            save_anonymized_text(anonymized, output_path=args.output_file)
            print(f"Anonymized text saved to '{args.output_file}'.")
        except Exception as e:
            print(f"Error writing to '{args.output_file}': {e}", file=sys.stderr)
            sys.exit(1)
    elif args.input_file:
        out_path = save_anonymized_text(anonymized, output_dir=os.path.dirname(args.input_file), original_filename=args.input_file)
        print(f"Anonymized text saved to '{out_path}'.")
    else:
        print(anonymized)


if __name__ == "__main__":
    main()
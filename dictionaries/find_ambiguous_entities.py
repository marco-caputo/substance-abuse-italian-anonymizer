import re
from typing import List, Set


def load_wordlist(path: str) -> Set[str]:
    """Load a newline-separated file into a lowercase set."""
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return {line.strip().lower() for line in f if line.strip()}


def find_ambiguous_entities(
    names_file: str,
    italian_words_file: str
) -> tuple[List[str], List[str]]:
    """
    Given a list of names and a list of Italian words:
    - Return a tuple: (ambiguous_names, non_ambiguous_names)

    Args:
        names_file: Path to the file containing names (one per line)
        italian_words_file: Path to Italian dictionary file (one per line)

    Returns:
        (ambiguous, not_ambiguous)
        ambiguous: names that ALSO appear in the Italian dictionary
        not_ambiguous: names that do NOT appear in the Italian dictionary
    """

    names_tokens = load_wordlist(names_file)
    italian_words_tokens = load_wordlist(italian_words_file)

    ambiguous = sorted(name for name in names_tokens if name in italian_words_tokens)
    not_ambiguous = sorted(name for name in names_tokens if name not in italian_words_tokens)

    return ambiguous, not_ambiguous

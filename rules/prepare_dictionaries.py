from typing import List

DICTIONARY_NAMES_TO_DISAMBIGUATE = ["cognomi", "comuni", "nazioni", "nomi", "regioni", "province"]
ITALIAN_WORDS_FILE = 'dictionaries/parole_it_60k.txt'


def load_wordlist(path: str, lower:bool = True) -> List[str]:
    """Load a newline-separated file into a lowercase set."""
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return [line.strip().lower() if lower else line.strip() for line in f if line.strip()]


def find_ambiguous_entities(names_file: str, italian_words_file: str) -> tuple[List[str], List[str]]:
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
    italian_words_tokens = set(load_wordlist(italian_words_file))

    # Sort by length descending to prioritize longer matches
    ambiguous = sorted([name for name in names_tokens if name in italian_words_tokens], key=len, reverse=True)
    not_ambiguous = sorted([name for name in names_tokens if name not in italian_words_tokens], key=len, reverse=True)

    return ambiguous, not_ambiguous

def seve_to_file(path: str, data: List[str]) -> None:
    """Save a list of strings to a txt file, one per line."""
    with open(path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(f"{item}\n")

def main():
    for dict_name in DICTIONARY_NAMES_TO_DISAMBIGUATE:
        names_file = f'dictionaries/{dict_name}_it.txt'
        ambiguous, not_ambiguous = find_ambiguous_entities(names_file, ITALIAN_WORDS_FILE)

        seve_to_file(f'dictionaries_processed/{dict_name}_it_ambiguous.txt', ambiguous)
        seve_to_file(f'dictionaries_processed/{dict_name}_it_not_ambiguous.txt', not_ambiguous)

if __name__ == "__main__":
    main()



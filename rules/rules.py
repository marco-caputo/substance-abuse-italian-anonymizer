import os
import re
import sys
from pathlib import Path

import unicodedata
import spacy
from spacy.tokens import Doc, Span
from typing import List

from rules.prepare_dictionaries import load_wordlist
from rules.remove_double_tags import merge_adjacent_entities_same_label

# Ensures project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

dictionaries_path = "rules/dictionaries"
processed_dictionaries_path = "rules/dictionaries_processed"

test_file_path =  os.path.join("test_files")
phone_text_path = os.path.join(test_file_path, "phone_text.txt")
email_text_path = os.path.join(test_file_path, "email_text.txt")
mixed_text_path = os.path.join(test_file_path, "mixed_text.txt")
url_text_path = os.path.join(test_file_path, "url_text.txt")
codes_text_path = os.path.join(test_file_path, "codes_text.txt")

gpe_tag = "GPE"
name_tag = "PER"
email_tag = "EMAIL"
phone_tag = "PHONE"
url_tag = "URL"
prov_tag = "PROV"
code_tag = "CODE"

simple_email_re = r"[A-Za-z0-9._%+-]+@+[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

phone_re = re.compile(r"""
(?<!\w)                             # not part of a word
(?=(?:.*\d){7,15})                  # require 7 to 15 digits total
(?:\+|00)?                          # optional leading + or 00
[\d\s().-]{7,25}                    # digits and allowed separators (space . ( ) -
(?:\s*(?:ext|x|extension)\s*\d{1,5})?  # optional extension
(?!\w)
""", re.VERBOSE | re.IGNORECASE)

tlds = (
    "com|org|net|edu|gov|mil|io|ai|it|fr|de|uk|us|co|info|biz|"
    "name|me|tv|cc|dev|app|tech|mobi|xyz|online|store|pro|int|"
    "eu|es|pt|ch|be|nl|se|no|dk|fi|ru"
)

urls_re = re.compile(r"""
(?:(?:https?|ftps?)://|//)?            # optional scheme or protocol-relative
(?:www\.)?                             # optional www.
(?:\S+(?::\S*)?@)?                     # optional user:pass@
(?:
  (?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+(?i:"""+tlds+r""")   # domain
  |
  \d{1,3}(?:\.\d{1,3}){3}             # IPv4
  |
  \[[0-9A-Fa-f:.]+\]                  # IPv6
)
(?::\d{2,5})?                         # optional port
(?:[/?#][^\s<>"]*)?                   # path, query, fragment
""", re.VERBOSE | re.IGNORECASE)

codes_re = re.compile(r"""
    (?:
        \b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b         # Codice Fiscale

      | \b[A-Z]{2,3}\d{5,7}[A-Z]{0,2}\b                    # CIE / Passport

      | \b[A-Z]\d{2}(?:\.[A-Z0-9]{1,4})?\b                 # ICD-10 style

      | (?<!\[)                                            # exclude inside [...]
        \b
        (?=[A-Z0-9-]{3,20}\b)                              # length 3–20, allow '-'
        (?=[A-Z0-9-]*[A-Z])                                # at least one letter
        (?=[A-Z0-9-]*\d)                                   # at least one digit
        (?!-)                                              # cannot start with '-'
        [A-Z0-9]+(?:-[A-Z0-9]+)*                           # alphanum groups separated by '-'
        \b
        (?!\])                                             # cannot end before ']'
    )
""", re.VERBOSE | re.IGNORECASE)


def _get_file_path(entities: str, ambiguous: bool = False) -> str:
    suffix = "ambiguous" if ambiguous else "not_ambiguous"
    return os.path.join(processed_dictionaries_path, f"{entities}_it_{suffix}.txt")


def _collect_entity_spans_from_regex(doc: Doc, regex: str | re.Pattern[str], tag: str, flags = 0) -> Doc:
    """
    Enriches the Doc with entities found by regex. Possible conflicts with existing entities are resolved by
    merging overlapping spans and preferring the longest span label.
    """
    # normalize to NFC so composed/decomposed forms match consistently
    text_nfc = unicodedata.normalize("NFC", doc.text)
    # collect spans for entities found by regex
    new_entities = []

    def replacer(match):
        start, end = match.start(), match.end()
        span = doc.char_span(start, end, label=tag, alignment_mode="expand")
        if span is not None:
            new_entities.append(span)

        return f"[{tag}]"

    re.sub(regex, replacer, text_nfc, flags=flags)

    # Combine existing entities and new entities
    all_spans = list(doc.ents) + new_entities
    if not all_spans:
        return doc

    # Sort spans by start index
    all_spans.sort(key=lambda s: s.start)

    # Merge overlapping spans
    merged_spans = []
    current = all_spans[0]
    for next_span in all_spans[1:]:
        if next_span.start <= current.end:  # overlap
            # merge: extend current span to cover both
            start = min(current.start, next_span.start)
            end = max(current.end, next_span.end)
            # optional: prefer longest span label
            label = current.label_ if (current.end - current.start) >= (
                        next_span.end - next_span.start) else next_span.label_
            current = Span(doc, start, end, label=label)
        else:
            merged_spans.append(current)
            current = next_span
    merged_spans.append(current)

    doc.ents = merged_spans

    return doc

def _mask_not_ambiguous_entities(doc: Doc, dictionary: List[str], tag: str, flags = 0) -> Doc:
    """
    Finds exact names from the given dictionary (case-insensitive, preserves accents).
    Longer names are placed first to avoid partial matches (e.g. 'Marco Antonio' before 'Marco').
    It is assumed that the dictionary is sorted by length descending.
    """
    if not dictionary:
        return doc

    pattern = r"\b(?:" + "|".join(re.escape(n) for n in dictionary) + r")\b"
    return _collect_entity_spans_from_regex(doc, pattern, tag, flags)


def _mask_ambiguous_entities(text: str, tokens: List[str], tag: str) -> str:
    if not tokens:
        return text

    text_nfc = unicodedata.normalize("NFC", text)
    capitalized_tokens = [t[0].upper() + t[1:] for t in tokens if t]
    sorted_tokens = sorted(set(capitalized_tokens), key=len, reverse=True)
    pattern = r"\b(?:" + "|".join(re.escape(t) for t in sorted_tokens) + r")\b"
    return re.sub(pattern, tag, text_nfc)


def _mask_ambiguous_province(doc: Doc, path: str) -> Doc:
    """Mask ambiguous province names by checking if they appear in capitalized form and are sorrounded by parentheses."""
    tokens = load_wordlist(path)
    if not tokens:
        return doc

    capitalized_tokens = [t.upper() for t in tokens if t]
    pattern = r"$((?:" + "|".join(re.escape(t) for t in capitalized_tokens) + r")$)"
    return _collect_entity_spans_from_regex(doc, pattern, prov_tag)


def _mask_entities_in_text(doc: Doc, file: str, tag: str) -> Doc:
    """
    Mask entities in the text using both not ambiguous and ambiguous masking.
    """
    not_ambiguous = load_wordlist(file)
    masked_doc = _mask_not_ambiguous_entities(doc, not_ambiguous, tag, re.IGNORECASE)
    return masked_doc


def apply_rules(doc: Doc | str) -> Doc:
    """
    Mask various entities in the text using unambiguous dictionaries and regex patterns.
    """
    if isinstance(doc, str):
        doc = Doc(spacy.blank("it").vocab, words=doc.split())

    doc = _mask_entities_in_text(doc, _get_file_path("nomi"), name_tag)
    doc = _mask_entities_in_text(doc, _get_file_path("cognomi"), name_tag)
    doc = _mask_entities_in_text(doc, _get_file_path("comuni"), gpe_tag)
    doc = _mask_entities_in_text(doc, _get_file_path("regioni"), gpe_tag)
    doc = _mask_entities_in_text(doc, _get_file_path("nazioni"), gpe_tag)

    doc = _collect_entity_spans_from_regex(doc, urls_re, url_tag)
    doc = _collect_entity_spans_from_regex(doc, codes_re, code_tag)
    doc = _collect_entity_spans_from_regex(doc, simple_email_re, email_tag, re.IGNORECASE)
    doc = _collect_entity_spans_from_regex(doc, phone_re, phone_tag)
    doc = _mask_entities_in_text(doc, _get_file_path("province"), prov_tag)
    doc = _mask_ambiguous_province(doc, _get_file_path("province", True))

    return merge_adjacent_entities_same_label(doc)
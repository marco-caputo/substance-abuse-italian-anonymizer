import os
import sys
from pathlib import Path
import regex as re

import unicodedata
import spacy
from spacy.tokens import Doc, Span
from typing import List
from config import PERSONAL_DATA_FORMAT

from rules.prepare_dictionaries import load_wordlist
from rules.merge_entities import merged_entity_spans

# Ensures project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

dictionaries_path = os.path.join(PROJECT_ROOT, "rules/dictionaries")
processed_dictionaries_path = os.path.join(PROJECT_ROOT, "rules/dictionaries_processed")

test_file_path =  os.path.join(PROJECT_ROOT, "rules/test_files")
phone_text_path = os.path.join(test_file_path, "phone_text.txt")
email_text_path = os.path.join(test_file_path, "email_text.txt")
mixed_text_path = os.path.join(test_file_path, "mixed_text.txt")
url_text_path = os.path.join(test_file_path, "url_text.txt")
codes_text_path = os.path.join(test_file_path, "codes_text.txt")

gpe_tag = "GPE"
per_tag = "PER"
email_tag = "MAIL"
phone_tag = "PHONE"
url_tag = "URL"
prov_tag = "PROV"
code_tag = "CODE"

common_ambiguous_names = "[Mm]arco|[Ll]uca|[Ff]rancesco|[Pp]aolo|[Pp]aolino|Pasquale|Omero|[Ll]aura|Linda|Aurora|[Dd]ante|[Dd]iana|[Mm]aria|[Ll]ucia|Bruno|Viola|Angelo|Angela|[Aa]ugusto|[Ss]ilvia|[Ss]ilvio|[Ss]andra|Roman[oa]|Diletta|Fede|[Ll]idia|Gloria|[Pp]iero|[Rr]enat[oa]|Franco|[Ll]eo|[Mm]attia|Marino|Giada|[Rr]occo|[Vv]anessa|[Ss]auro|[Aa]lessia|Violetta|Massimo|[Cc]laudia|[Vv]eronica|[Vv]ittorio|Vittoria|[Pp]enelope|[Pp]atrizi[oa]|[Gg]raziano|Grazia|Cristian[oa]|[Ff]ilippo|[Ff]abiano|[Mm]oira|[Rr]affaella|[Ee]lisa|[Ll]isa|[Ll]azzaro|[Gg]iacinto|Salvatore|Stella|Fausto|[Tt]iziano|[Mm]immo|Italo|Guido|[Ii]do|[Mm]aia|Luna|[Cc]iro|[Cc]aio|[Aa]melia|[Mm]elissa|Gustavo"

email_re = r"[A-Za-z0-9._%+-]+@+[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

phone_re = re.compile(r"""
(?:(?<=^)|(?<=[\s.,;:()]))                                        # allowed delimiter
(?!\()                                                            # do not allow ( as first character
(?![-\s()]*\d{1,2}[-/]\d{1,2}[-/]\d{2,4}(?:\s+\d{2}:\d{2})?)      # Reject dates
(?=(?:.*\d){7,15})
(?:\+|00)?                                                        # optional leading + or 00
[\d\s().\-\/]{7,25}                                               # digits + separators
(?:\s*(?:ext|x|extension)\s*\d{1,5})?
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
  (?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+(?:"""+tlds+r""")   # domain
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
    
      | \b\d{5}\b                                          # CAP code

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


def _collect_entity_spans_from_regex(doc: Doc, pattern: str | re.Pattern[str], tag: str, flags = 0) -> list[Span]:
    """
    Enriches the Doc with entities found by regex. Possible conflicts with existing entities are resolved by
    merging overlapping spans and preferring the longest span label.
    """
    # normalize to NFC so composed/decomposed forms match consistently
    text_nfc = unicodedata.normalize("NFC", doc.text)
    # collect spans for entities found by regex
    new_entities = []

    def replacer(match):
        start, end = (match.start(1), match.end(1)) if match.lastindex else (match.start(), match.end())
        span = doc.char_span(start, end, label=tag, alignment_mode="expand")
        if span is not None:
            new_entities.append(span)

        return f"[{tag}]"

    re.sub(pattern, replacer, text_nfc, flags=flags)

    return new_entities

def _mask_not_ambiguous_entities(doc: Doc, dictionary: List[str], tag: str, flags = 0) -> list[Span]:
    """
    Finds exact names from the given dictionary (case-insensitive, preserves accents).
    Longer names are placed first to avoid partial matches (e.g. 'Marco Antonio' before 'Marco').
    It is assumed that the dictionary is sorted by length descending.
    """
    if not dictionary:
        return []

    pattern = r"\b(?:" + "|".join(re.escape(n) for n in dictionary) + r")\b"
    return _collect_entity_spans_from_regex(doc, pattern, tag, flags)


def _mask_ambiguous_entities(doc: Doc, dictionary: List[str], tag: str, flags = 0) -> list[Span]:
    if not dictionary:
        return []

    capitalized_dic = [t.capitalize() for t in dictionary if t]
    capitalized_dic += [t.upper() for t in dictionary if t]
    pattern = ( # ensure not at start of sentence or after punctuation or paragraph break
            r"(?<!^)"
            r"(?<!\n[\s\t]*\n[\s\t\n]*)"
            r"(?<![-\.!?:;·…»«>\n][\s\t\n]*)"
            r"\b(?:" + "|".join(re.escape(t) for t in capitalized_dic) + r")\b"
    )
    return _collect_entity_spans_from_regex(doc, pattern, tag, flags)


def _mask_province(doc: Doc, path: str, ambiguous: bool) -> list[Span]:
    """Mask province names by checking if they appear in capitalized form. If ambiguous, also check they are sorrounded by parentheses."""
    tokens = load_wordlist(path)
    if not tokens:
        return []

    capitalized_tokens = [t.upper() for t in tokens if t]
    pattern = r"\(\s*(" + "|".join(re.escape(t) for t in capitalized_tokens) + r")\s*\)" if ambiguous \
        else r"\b(" + "|".join(re.escape(t) for t in capitalized_tokens) + r")\b"
    return _collect_entity_spans_from_regex(doc, pattern, prov_tag)

def _mask_ambiguous_common_names(doc: Doc) -> list[Span]:
    """
    Mask common ambiguous names according to the regex capitalization in any possible position (even start of sentence).
    """
    pattern = r"\b(?:" + common_ambiguous_names + r")\b"
    return _collect_entity_spans_from_regex(doc, pattern, per_tag)


def _mask_entities_in_text(doc: Doc, file: str, tag: str, ambguous: bool = False) -> list[Span]:
    """
    Mask entities in the text using both not ambiguous and ambiguous masking.
    """
    word_list = load_wordlist(file)
    masked_ents = _mask_ambiguous_entities(doc, word_list, tag) if ambguous \
        else _mask_not_ambiguous_entities(doc, word_list, tag, re.IGNORECASE)

    return masked_ents


def _mask_personal_data(doc: Doc, personal_data: dict[str, str]) -> list[Span]:
    """Mask personal data in the text using the provided dictionary."""
    new_entities = []
    for key, label in PERSONAL_DATA_FORMAT.items():
        if key in personal_data:
            pattern = r"\b" + re.escape(personal_data[key]) + r"\b"
            flag = re.IGNORECASE if label != "PROV" else 0
            new_entities += _collect_entity_spans_from_regex(doc, pattern, label, flag)

    return new_entities


def apply_rules(doc: Doc | str, per_matching:bool = True, personal_data:dict[str, str] = None) -> Doc:
    """
    Mask various entities in the text using dictionaries and regex patterns.

    :param doc: The spaCy Doc object or raw text to process.
    :param per_matching: Whether to anonymize PER and PATIENT entities in combination with dictionaries
    :param personal_data: A dictionary of personal data to make specific masking
    """
    if isinstance(doc, str):
        doc = Doc(spacy.blank("it").vocab, words=doc.split())

    new_entities = []

    if personal_data:
        new_entities += _mask_personal_data(doc, personal_data)

    new_entities += _collect_entity_spans_from_regex(doc, email_re, email_tag, re.IGNORECASE)
    new_entities += _collect_entity_spans_from_regex(doc, urls_re, url_tag)

    if per_matching:
        new_entities += _mask_entities_in_text(doc, _get_file_path("nomi"), per_tag)
        new_entities += _mask_entities_in_text(doc, _get_file_path("nomi", True), per_tag, ambguous=True)
        new_entities += _mask_ambiguous_common_names(doc)
        new_entities += _mask_entities_in_text(doc, _get_file_path("cognomi"), per_tag)
        new_entities += _mask_entities_in_text(doc, _get_file_path("cognomi", True), per_tag, ambguous=True)
        new_entities += _mask_entities_in_text(doc, _get_file_path("comuni"), gpe_tag)
        new_entities += _mask_entities_in_text(doc, _get_file_path("comuni", True), gpe_tag, ambguous=True)

    new_entities += _mask_entities_in_text(doc, _get_file_path("regioni"), gpe_tag)
    new_entities += _mask_entities_in_text(doc, _get_file_path("nazioni"), gpe_tag)

    new_entities += _collect_entity_spans_from_regex(doc, phone_re, phone_tag)
    new_entities += _collect_entity_spans_from_regex(doc, codes_re, code_tag)
    new_entities += _mask_province(doc, _get_file_path("province", False), False)
    new_entities += _mask_province(doc, _get_file_path("province", True), True)

    return merged_entity_spans(new_entities, doc)

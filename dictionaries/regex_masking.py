import os
import re

import unicodedata
from typing import List, Tuple


gpe_tag = "[GPE]"
name_tag = "[PER]"
email_tag = "[EMAIL]"
phone_tag = "[PHONE]"
url_tag = "[URL]"
prov_tag = "[PROV]"
code_tag = "[CODE]"

test_file_path = "test_files"
phone_text_path = os.path.join(test_file_path, "phone_text.txt")
email_text_path = os.path.join(test_file_path, "email_text.txt")
mixed_text_path = os.path.join(test_file_path, "mixed_text.txt")
url_text_path = os.path.join(test_file_path, "url_text.txt")
codes_text_path = os.path.join(test_file_path, "codes_text.txt")

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

phone_text = read_file(phone_text_path)
email_text = read_file(email_text_path)
mixed_text = read_file(mixed_text_path)
url_text = read_file(url_text_path)
codes_text = read_file(codes_text_path)

dictionaries_path = "dictionaries"
municipalities_file_path = os.path.join(dictionaries_path, "comuni_it.txt")
nations_file_path = os.path.join(dictionaries_path, "nazioni_it.txt")
names_file_path = os.path.join(dictionaries_path, "nomi_it.txt")
provinces_file_path = os.path.join(dictionaries_path, "province_it.txt")
regions_file_path = os.path.join(dictionaries_path, "regioni_it.txt")



def tokenize_file(file_path):
    tokens_set = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            token = line.strip()
            if token:
                tokens_set.append(token)
    return tokens_set

nations_dict = tokenize_file(nations_file_path)
provinces_dict = tokenize_file(provinces_file_path)
regions_dict = tokenize_file(regions_file_path)
municipalities_dict = tokenize_file(municipalities_file_path)
names_dict = tokenize_file(names_file_path)


def mask_entities_from_dict(text: str, dictionary: List[str], tag: str, flags = 0) -> str:
    """
    Mask exact names from `names` list (case-insensitive, preserves accents).
    Longer names are placed first to avoid partial matches (e.g. 'Marco Antonio' before 'Marco').
    """
    if not dictionary:
        return text
    # normalize to NFC so composed/decomposed forms match consistently
    text_nfc = unicodedata.normalize("NFC", text)
    # sort by length desc to prefer multi-word/longer names
    names_sorted = sorted(set(dictionary), key=len, reverse=True)
    pattern = r"\b(?:" + "|".join(re.escape(n) for n in names_sorted) + r")\b"
    return re.sub(pattern, tag, text_nfc, flags=flags)



result = mask_entities_from_dict(mixed_text, nations_dict, gpe_tag, re.IGNORECASE)
result = mask_entities_from_dict(result, regions_dict, gpe_tag, re.IGNORECASE)
result = mask_entities_from_dict(result, municipalities_dict, gpe_tag, re.IGNORECASE)
result = mask_entities_from_dict(result, provinces_dict, prov_tag)
result = mask_entities_from_dict(result, names_dict, name_tag, re.IGNORECASE)
print(result)

simple_email_re = r"[A-Za-z0-9._%+-]+@+[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
masked_email_text = re.sub(simple_email_re, email_tag, email_text, flags=re.IGNORECASE)
print(masked_email_text)

phone_re = re.compile(r"""
(?<!\w)                             # not part of a word
(?=(?:.*\d){7,15})                  # require 7 to 15 digits total
(?:\+|00)?                          # optional leading + or 00
[\d\s().-]{7,25}                    # digits and allowed separators (space . ( ) -
(?:\s*(?:ext|x|extension)\s*\d{1,5})?  # optional extension
(?!\w)
""", re.VERBOSE | re.IGNORECASE)


masked_phone_text = re.sub(phone_re, phone_tag, phone_text)
print(masked_phone_text)


urls_re = re.compile(r"""
(?:(?:https?|ftps?)://|//)?            # optional scheme or protocol-relative
(?:www\.)?                             # optional www.
(?:\S+(?::\S*)?@)?                     # optional user:pass@
(?:
  (?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,}  # domain
  |
  \d{1,3}(?:\.\d{1,3}){3}             # IPv4
  |
  \[[0-9A-Fa-f:.]+\]                  # IPv6
)
(?::\d{2,5})?                         # optional port
(?:[/?#][^\s<>"]*)?                   # path, query, fragment
""", re.VERBOSE | re.IGNORECASE)

masked = re.sub(urls_re, url_tag, url_text)
print(masked)



pattern = re.compile(
    r'\b[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]\b|'   # Italian tax code
    r'\b[A-Z]{2,3}[0-9]{5,7}[A-Z]{0,2}\b|'                      # CIE, ID cartacea, passport
    r'\b[A-Z][0-9]{2}(?:\.[0-9A-Z]{1,4})?\b|'                  # ICD-10 code
    r'\b(?=[A-Z0-9]{3,20}\b)(?=.*\d)[A-Z0-9]+\b',               # Generic alphanumeric (must contain at least one number)
)
masked_codes_text = re.sub(pattern, code_tag, codes_text)
print(masked_codes_text)




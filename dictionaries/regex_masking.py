import os
import re

import unicodedata
from typing import List, Tuple
from find_ambiguous_entities import find_ambiguous_entities

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


def mask_not_ambiguous_entities(text: str, dictionary: List[str], tag: str, flags = 0) -> str:
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

simple_email_re = r"[A-Za-z0-9._%+-]+@+[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

phone_re = re.compile(r"""
(?<!\w)                             # not part of a word
(?=(?:.*\d){7,15})                  # require 7 to 15 digits total
(?:\+|00)?                          # optional leading + or 00
[\d\s().-]{7,25}                    # digits and allowed separators (space . ( ) -
(?:\s*(?:ext|x|extension)\s*\d{1,5})?  # optional extension
(?!\w)
""", re.VERBOSE | re.IGNORECASE)

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

def mask_ambiguous_entities(text: str, tokens: List[str], tag: str) -> str:
    if not tokens:
        return text

    text_nfc = unicodedata.normalize("NFC", text)
    capitalized_tokens = [t[0].upper() + t[1:] for t in tokens if t]
    sorted_tokens = sorted(set(capitalized_tokens), key=len, reverse=True)
    pattern = r"\b(?:" + "|".join(re.escape(t) for t in sorted_tokens) + r")\b"
    return re.sub(pattern, tag, text_nfc)


def mask_entities_in_text(text: str, file: str, compare_to_file: str, tag: str ) -> str:
    """
    Mask entities in the text using both not ambiguous and ambiguous masking.
    """
    ambiguous, not_ambiguous = find_ambiguous_entities(
        file,
        compare_to_file
    )
    masked_text = mask_not_ambiguous_entities(text, not_ambiguous, tag, re.IGNORECASE)
    masked_text = mask_ambiguous_entities(masked_text, ambiguous, tag)
    return masked_text



def mask_text(text: str) -> str:
    """
    Mask various entities in the text using predefined dictionaries and regex patterns.
    """
    italian_words_file = 'github_dictionaries/660000_parole_italiane.txt'
    ambiguous, not_ambiguous = find_ambiguous_entities(
        'dictionaries/comuni_it.txt',
        'github_dictionaries/660000_parole_italiane.txt'
    )
    masked_text = mask_not_ambiguous_entities(text, not_ambiguous, gpe_tag, re.IGNORECASE)
    masked_text = mask_ambiguous_entities(masked_text, ambiguous, gpe_tag)
    # masked_text = mask_entities_in_text(text, municipalities_file_path, italian_words_file, gpe_tag)

    ambiguous, not_ambiguous = find_ambiguous_entities(
        'dictionaries/regioni_it.txt',
        'github_dictionaries/660000_parole_italiane.txt'
    )
    masked_text = mask_not_ambiguous_entities(masked_text, not_ambiguous, gpe_tag, re.IGNORECASE)
    masked_text = mask_ambiguous_entities(masked_text, ambiguous, gpe_tag)

    ambiguous, not_ambiguous = find_ambiguous_entities(
        'dictionaries/nazioni_it.txt',
        'github_dictionaries/660000_parole_italiane.txt'
    )
    masked_text = mask_not_ambiguous_entities(masked_text, not_ambiguous, gpe_tag, re.IGNORECASE)
    masked_text = mask_ambiguous_entities(masked_text, ambiguous, gpe_tag)

    ambiguous, not_ambiguous = find_ambiguous_entities(
        'dictionaries/nomi_it.txt',
        'github_dictionaries/660000_parole_italiane.txt'
    )
    masked_text = mask_not_ambiguous_entities(masked_text, not_ambiguous, name_tag, re.IGNORECASE)
    masked_text = mask_ambiguous_entities(masked_text, ambiguous, name_tag)

    ambiguous, not_ambiguous = find_ambiguous_entities(
        'github_dictionaries/lista_cognomi.txt',
        'github_dictionaries/660000_parole_italiane.txt'
    )
    masked_text = mask_not_ambiguous_entities(masked_text, not_ambiguous, name_tag, re.IGNORECASE)
    masked_text = mask_ambiguous_entities(masked_text, ambiguous, name_tag)
    masked_text = re.sub(urls_re, url_tag, masked_text)

    masked_text = re.sub(codes_re, code_tag, masked_text)

    masked_text = mask_not_ambiguous_entities(masked_text, provinces_dict, prov_tag)

    masked_text = re.sub(simple_email_re, email_tag, masked_text, flags=re.IGNORECASE)
    masked_text = re.sub(phone_re, phone_tag, masked_text)
    return masked_text


testo = """
Nel mese di settembre 2024, Marco Rossi ha partecipato a una conferenza sulla sicurezza informatica organizzata a Milano, in Lombardia, con ospiti provenienti non solo dall’Italia, ma anche dalla Francia, dalla Germania e perfino dal Giappone. Durante l’evento, il professor Giulia Bianchi, esperta di crittografia e docente presso l’Università di Torino (Piemonte), ha illustrato alcuni casi pratici avvenuti nella municipalità di Bologna e nella provincia di Firenze, in Toscana.

Tra gli interventi più attesi c’era quello del ricercatore indipendente Luca Verdi, che ha presentato un report dettagliato su oltre 300 violazioni dei dati avvenute tra il 2020 e il 2023. Nel rapporto comparivano vari riferimenti a codici interni come USR-492A, CODX-11-FF, e SYS2024-BETA.

Per chi desiderava ricevere maggiori informazioni, era possibile scrivere all’indirizzo email info@sicurezzait.org o contattare l’assistenza tecnica al numero +39 347 889 2211, attivo anche tramite WhatsApp. Inoltre, tutto il materiale della conferenza può essere scaricato dal sito ufficiale: https://www.cyberconf2024.it/documenti/materiale. Alcuni partecipanti hanno anche segnalato link di risorse aggiuntive come http://blog-ricerca.net/articoli e www.sicurezzaonline.it.

Un altro intervento interessante è stato quello di Anna Marino, responsabile della regione Sicilia, che ha raccontato un caso relativo alla città di Catania. In questa occasione è stato menzionato anche il codice identificativo locale CT-99211, utilizzato per tracciare alcune segnalazioni.

Per garantire l’anonimato nei report interni, gli organizzatori hanno utilizzato un sistema automatico che sostituisce nomi e luoghi con tag specifici. Ad esempio, i dati sensibili come indirizzi email, numeri di telefono e URL devono essere sempre mascherati attraverso apposite funzioni di sanitizzazione.
"""

print(mask_text(testo))
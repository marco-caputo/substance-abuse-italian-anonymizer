import os
from typing import Iterable

from spacy.tokens import Doc
from docx import Document
from PyPDF2 import PdfReader

from config import PATIENT_DATA_FIELDS, SINGLE_TEXT_FIELDS
from utils.json_utils import read_json_file

def anonymize_doc(doc: Doc, labels_to_anonymize: Iterable[str]=None) -> str:
    """
    Returns anonymized text where selected entity labels are replaced by [LABEL].

    :param doc: spaCy Doc
    :param labels_to_anonymize: Iterable of entity labels to anonymize (e.g. {"PER", "LOC"})
                                If None, anonymizes ALL entities.
    """
    labels_to_anonymize = set(ent.label_ for ent in doc.ents) if labels_to_anonymize is None else set(labels_to_anonymize)
    text = doc.text

    # collect only entities whose label is in the allowed set
    offsets = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents if ent.label_ in labels_to_anonymize]
    offsets.sort(reverse=True) # Replace from end to beginning to preserve offsets

    for start, end, label in offsets:
        text = text[:start] + f"[{label}]" + text[end:]

    return text

def save_anonymized_text(text:str, output_path=None, output_dir=None, original_filename=None) -> str:
    """Saves anonymized text to a .txt file and returns the output path."""
    if output_path:
        out_path = output_path
    elif output_dir and original_filename:
        base_name = os.path.splitext(os.path.basename(original_filename))[0]
        out_path = os.path.join(output_dir, f"{base_name}_anonymized.txt")
    else:
        return

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    return out_path

def save_many_texts(texts: list[str], output_dir: str, original_filename: str):
    """Saves multiple anonymized texts to separate files in the specified directory."""
    base_name = os.path.splitext(os.path.basename(original_filename))[0]
    os.makedirs(output_dir, exist_ok=True)

    if len(texts) == 1:
        return save_anonymized_text(texts[0], output_dir=output_dir, original_filename=original_filename)
    else:
        for i, text in enumerate(texts):
            out_path = os.path.join(output_dir, f"{base_name}_anonymized_{i + 1}.txt")
            save_anonymized_text(text, output_path=out_path, original_filename=original_filename)
        return output_dir

def read_file(file_path) -> tuple[list[str], dict[str,str]|None]:
    """Reads a file and returns its text content in form of a list of texts, combined with an optional dictionary of personal data."""
    ext = os.path.splitext(file_path)[1].lower()
    dict = None

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            texts = [f.read()]
    elif ext == ".docx":
        doc = Document(file_path)
        texts = ["\n".join([para.text for para in doc.paragraphs])]
    elif ext == ".pdf":
        reader = PdfReader(file_path)
        texts = ["\n".join([page.extract_text() or "" for page in reader.pages])]
    elif ext == ".json":
        data = read_json_file(file_path)
        try:
            texts = [text[SINGLE_TEXT_FIELDS[1]] for text in data[PATIENT_DATA_FIELDS[1]]]
        except IndexError:
            raise ValueError(f"JSON file must contain a '{PATIENT_DATA_FIELDS[1]}' field consisting in a list of entries with '{SINGLE_TEXT_FIELDS[1]}' fields.")
        try:
            dict = data[PATIENT_DATA_FIELDS[0]]
        except KeyError:
            raise ValueError(f"JSON file must contain a '{PATIENT_DATA_FIELDS[0]}' field with personal data dictionary.")
    else:
        raise ValueError("Unsupported file type.")

    return texts, dict

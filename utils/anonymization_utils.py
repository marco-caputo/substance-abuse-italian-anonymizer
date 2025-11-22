import os
from typing import Iterable
from spacy.tokens import Doc
from docx import Document
from PyPDF2 import PdfReader

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

def save_anonymized_text(text:str, output_path=None, output_dir=None, original_filename=None):
    """Saves anonymized text to a .txt file."""
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

def read_file(file_path):
    """Reads a file and returns its text content."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    elif ext == ".docx":
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
    elif ext == ".pdf":
        reader = PdfReader(file_path)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
    else:
        raise ValueError("Unsupported file type.")
    return text

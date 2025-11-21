import spacy
from data_generation import NER_LABELS
from rules.regex_masking import mask_text
from rules.remove_double_tags import remove_double_tags

def anonymize_text(nlp_model, text, entities_to_anonymize):
    """Replaces selected entity types with anonymized placeholders."""
    doc = nlp_model(text)
    anonymized = text
    offset = 0

    for ent in doc.ents:
        if ent.label_ in entities_to_anonymize:
            start, end = ent.start_char + offset, ent.end_char + offset
            replacement = f"[{ent.label_}]"
            anonymized = anonymized[:start] + replacement + anonymized[end:]
            offset += len(replacement) - (end - start)

    return anonymized

def get_full_anonymizer(path: str):
    """Returns a full anonymization function using the specified spaCy model path."""
    nlp = spacy.load(path)
    return lambda txt: remove_double_tags(mask_text(anonymize_text(nlp, txt, NER_LABELS)))


if __name__ == "__main__":
    from pathlib import Path
    model_path = "../NER/models/fine_tuned/gpu/model2_best/"

    nlp_anonymizer = get_full_anonymizer(model_path)
    sample_text = "Il Mario Rossi vive a Roma e il suo codice fiscale è RSSMRA85M01H501U."
    anonymized_text = nlp_anonymizer(sample_text)
    print("Original Text:")
    print(sample_text)
    print("\nAnonymized Text:")
    print(anonymized_text)
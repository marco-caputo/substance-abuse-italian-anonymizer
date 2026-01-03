import re

from spacy.tokens import Doc, Span

gpe_tag = "[GPE]"
name_tag = "[PER]"
email_tag = "[MAIL]"
phone_tag = "[PHONE]"
url_tag = "[URL]"
prov_tag = "[PROV]"
code_tag = "[CODE]"


label_patterns = {  # label_patterns for merging overlapping or adjacent entities
    ("PER", "PATIENT"): "PATIENT",
    ("PATIENT", "PER"): "PATIENT",
    ("LOC", "GPE"): "LOC",
    ("FAC", "GPE"): "FAC",
    ("ORG", "FAC"): "ORG",
    ("FAC", "ORG"): "ORG",
    ("ORG", "MAIL"): "MAIL",
    ("EMAIL", "ORG"): "MAIL",
    ("PER", "MAIL"): "MAIL",
    ("EMAIL", "PER"): "MAIL",
    ("URL", "ORG"): "URL",
    ("ORG", "URL"): "URL"
}

def merged_entity_spans(new_entities: list[Span], doc: Doc) -> Doc:
    """
    Merges overlapping spans of the given doc emerging from the new entities, splitting spans in non-overlapping parts
    in the general case and merging adjacent or space-separated spans with the same label or according to predefined patterns.
    """
    all_spans = list(doc.ents) + new_entities
    if not all_spans:
        return doc

    all_spans.sort(key=lambda s: s.start)

    merged_spans = []
    current = all_spans[0]
    for next_span in all_spans[1:]:
        single_space = doc[current.end:next_span.start].text == " "

        # --- overlap ---
        if next_span.start < current.end:
            if next_span.end < current.end:
                continue  # contained, drop next_span
            elif current.start == next_span.start and next_span.end > current.end:
                current = next_span  # contained, keep next_span
                continue
            label = label_patterns.get((current.label_, next_span.label_))
            if label:  # pattern-based merge
                new = Span(doc, current.start, next_span.end, label=label)
            else:  # fallback: keep longest label
                longest = current if (current.end-current.start) >= (next_span.end-next_span.start) else next_span
                new = Span(doc, current.start, next_span.end, label=longest.label_)

            if new is not None:
                current = new
            continue

        # --- adjacent/space-separated ---
        if next_span.start == current.end or single_space:
            if current.label_ == next_span.label_:
                label = current.label_
            else:
                label = label_patterns.get((current.label_, next_span.label_))

            if label:
                new = Span(doc, current.start, next_span.end, label=label)
                if new is not None:
                    current = new
                continue

        # --- no overlap ---
        merged_spans.append(current)
        current = next_span

    merged_spans.append(current)
    doc.ents = merged_spans
    return doc


def remove_double_tags(text: str) -> str:
    """
    Remove double tags from a masked text string.
    For example, it converts "[PER][PER]" to "[PER]".
    """
    patterns = [
        (r'(\[PER\]\s*){2,}', name_tag),
        (r'(\[GPE\]\s*){2,}', gpe_tag),
        (r'(\[EMAIL\]\s*){2,}', email_tag),
        (r'(\[PHONE\]\s*){2,}', phone_tag),
        (r'(\[URL\]\s*){2,}', url_tag),
        (r'(\[PROV\]\s*){2,}', prov_tag),
        (r'(\[CODE\]\s*){2,}', code_tag),
    ]

    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)


    return add_spaces_after_tags(text)

def add_spaces_after_tags(text: str) -> str:
    """
    Ensure there is a space after each tag if not already present.
    Only if there isn't a punctuation or space after the tag.
    For example, it converts "[PER]John Doe" to "[PER] John Doe".
    """
    tags = [name_tag, gpe_tag, email_tag, phone_tag, url_tag, prov_tag, code_tag]
    for tag in tags:
        # Use (?=\w) to look for a word character (letter/number/underscore)
        pattern = re.escape(tag) + r'(?=\w)'
        replacement = tag + ' '
        text = re.sub(pattern, replacement, text)
    return text

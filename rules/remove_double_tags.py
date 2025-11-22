import re

from spacy.tokens import Doc, Span

gpe_tag = "[GPE]"
name_tag = "[PER]"
email_tag = "[EMAIL]"
phone_tag = "[PHONE]"
url_tag = "[URL]"
prov_tag = "[PROV]"
code_tag = "[CODE]"


def merge_adjacent_entities_same_label(doc: Doc) -> Doc:
    """Merge entities that are either adjacent or separated by a single space only if they share the same label."""
    if not doc.ents:
        return doc

    # Sort entities by start index
    ents_sorted = sorted(doc.ents, key=lambda e: e.start)

    merged_spans = []
    current = ents_sorted[0]

    for next_ent in ents_sorted[1:]:
        # Check token gap and text between
        gap = next_ent.start - current.end
        text_between = doc[current.end:next_ent.start].text
        single_space = text_between == " "

        # Merge only if labels are the same
        if (gap == 0 or single_space) and current.label_ == next_ent.label_:
            # Merge spans
            start = current.start
            end = next_ent.end
            current = Span(doc, start, end, label=current.label_)
        else:
            merged_spans.append(current)
            current = next_ent

    merged_spans.append(current)

    # Assign merged spans back to doc.ents
    doc.ents = merged_spans
    return doc


def remove_double_tags(text: str) -> str:
    """
    Remove double tags from a masked text string.
    For example, it converts "[PER][PER] John Doe [PER][PER]" to "[PER] John Doe [PER]".
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

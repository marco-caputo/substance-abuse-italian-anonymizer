import re

gpe_tag = "[GPE]"
name_tag = "[PER]"
email_tag = "[EMAIL]"
phone_tag = "[PHONE]"
url_tag = "[URL]"
prov_tag = "[PROV]"
code_tag = "[CODE]"

def remove_double_tags(text: str) -> str:
    """
    Remove double tags from the text.
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

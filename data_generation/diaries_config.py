from config import  ENTITIES
NUMBER_OF_SAMPLES_TO_GENERATE = 5

SAMPLES = [] # Missing sample insertion.

PROMPT = f"""You are tasked with generating synthetic training data for a Named Entity Recognition (NER) system that 
processes Italian diary entries with medical and personal content.

Goal:
Produce exactly {NUMBER_OF_SAMPLES_TO_GENERATE} diverse diary-style samples in Italian that naturally include 
the entity labels below.
You can take inspiration from the following examples but do NOT copy them, instead create entirely new diary entries.
The following samples always refer to what happened yesterday (i.e., the day before the diary entry date), 
feel free to change the details and the context, these are just for inspiration It's fundamental that you create
original content, but diaries have to remain realistic and plausible.
Samples:\n
{"\n".join(f"-{sample}" for sample in SAMPLES)}\n
Don't be afraid to vary the style, content of the entries; be creative
but ensure the inserted entities fit naturally within the context of each diary entry.

Possible entities that can be included are:
{"\n".join([f"- {e["label"]}: {e["desc"]}" for e in ENTITIES])}\n

Strict requirements:
1. Vary labels: do not use the same subset of labels in every entry; rotate combinations across samples and 
within entries. Use 2–5 entities per entry, but vary the count. 
2. Diverse examples: when reusing the same label across different entries, use different concrete examples each 
time.
3. Coherence: after inserting entities, the diary text must remain natural and plausible in idiomatic Italian.
4. Faithful spans: every entity span in "entities" must appear verbatim in the "text" and match exactly the intended mention.
5. Label semantics: respect label meanings (e.g., PATIENT is the patient’s name/surname; PER are other named people; 
AGE is an age mention like "42 anni"; DATE are explicit dates/time; GPE vs. LOC as defined).
6. No leakage: output only the JSON array with exactly {NUMBER_OF_SAMPLES_TO_GENERATE} items; no extra commentary, headers, or code fences.
7. JSON correctness: valid JSON with double quotes, no trailing commas, and correct arrays/objects.

Always respond with data samples that follow exactly this format, with no text before or after the JSON:

[
  {{
    "text": "full diary of what he did yesterday",
    "entities": [
      {{
        "text": "string, the entity span from the text",
        "label": "string, the NER label for this entity"
      }}
    ]
  }}
]

Ensure correct JSON syntax, no explanations, and no Markdown code fences."""


if __name__ == "__main__":
    print(PROMPT)
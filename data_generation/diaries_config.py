NUMBER_OF_SAMPLES_TO_GENERATE = 20

SEED_PATH = "seed_samples/translated_data_it.csv"
NUMBER_OF_ROWS = 20

SYSTEM_PROMPT = """
You are tasked with generating synthetic training data for a Named Entity Recognition (NER) system that 
processes Italian diary entries with medical and personal content. Your task requires you to take existing diaries
and insert named entities naturally into the text, ensuring that the entries remain coherent and realistic.

Always respond with data samples that follow exactly this format, with no text before or after the JSON:

[
  {{
    "text": "full diary",
    "entities": [
      {{
        "text": "string, the entity span from the text",
        "label": "string, the NER label for this entity"
      }}
    ]
  }}
]

Ensure correct JSON syntax, no explanations, and no Markdown code fences.
"""

SEED_SAMPLE = {
    "filename": "diaries_it.csv",
    "description": "diary entry in Italian",
    "additional_instructions": """
Goal:
Take the examples listed below and insert named entities into each diary entry while keeping the text coherent, 
realistic, and idiomatic in Italian. Ensure entities are integrated naturally into the narrative and, most 
importantly, that the diary entries remain plausible and believable.

Strict requirements:
- Vary labels: do not use the same subset of labels in every entry; rotate combinations across samples and 
  within entries. Use 2–5 entities per entry, but vary the count.
- Diverse examples: when reusing the same label across different entries, use different concrete examples 
  each time.
- Coherence: after inserting entities, the diary text must remain natural and plausible in idiomatic Italian.
- Label semantics: respect label meanings (PER are named people; AGE is an age mention like "42 anni"; 
  DATE are explicit dates/time; GPE vs. LOC as defined).
- Do not limit to appending entities at the end of given diary note, instead integrate them naturally within the text.
- If an expression is not sound in Italian, modify it to make it idiomatic while keeping the original meaning.

For instance the following diary entry:
Ieri ho sentito l'importanza della mia salute. Ho fatto un'escursione un po' più lunga del solito e sono stata molto felice di poterla fare. Mi ha fatto apprezzare la mia salute. Con tutte le notizie di persone che muoiono e la tragedia dell'omicidio della famiglia Utah in Messico, mi ha reso davvero consapevole dell'importanza della mia salute e del mio benessere.

Can be transformed into:
{{
    "text": "Ieri ho riscoperto l'importanza della salute. Ho fatto un'escursione nel Parco del Gran Sasso e sono stata molto felice di poterla fare. Mi ha fatto stare bene. Con tutte le notizie di persone che muoiono e la tragedia dell'omicidio della famiglia Utah in Messico, mi ha reso davvero consapevole dell'importanza della mia salute e del mio benessere.",
    "entities": [
      {{
        "text": "Parco del Gran Sasso",
        "label": "LOC"
      }},
      {{
          "text": "Utah",
          "label": "PER"
      }},
      {{
          "text": "Messico",
          "label": "GPE"
      }}
    ]
  }}
"""
}
SEED_SAMPLES = [           # Files to use as seed examples
    {
        "filename": 'seed_diaries.json',
        "description": "clinical diary note",
        "n_outputs": 2},
    {
        "filename": 'seed_reports.json',
        "description": "therapy report",
        "n_outputs": 2}
]
N_PER_OUTPUT = 5            # Number of samples to generate per model output
ENTITIES = [                # Possible NER labels
    "PATIENT_NAME",
    "AGE",
    "SUBSTANCE",
    "DATE",
    "LOCATION",
    "DURATION"
]
SYSTEM_PROMPT = """
You generate realistic synthetic Italian therapy reports for patients in substance abuse treatment.
Each report is NER-labeled and returned strictly in JSON format.

Always respond with data samples that follow exactly this format, with no text before or after the JSON:

[
  {
    "text": "string, the full therapy report in Italian",
    "entities": [
      {
        "text": "string, the entity span from the text",
        "label": "string, the NER label (e.g. PATIENT_NAME, AGE, SUBSTANCE, DATE, LOCATION, DURATION)"
      }
    ]
  },
]

Ensure correct JSON syntax, no explanations, and no Markdown code fences.
"""
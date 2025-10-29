SEED_SAMPLES = [           # Files to use as seed examples
    {
        "filename": 'seed_diaries_psych.json',
        "description": "psychiatric clinical diary note",
        "additional_instructions": "Please, make sure to use a variety of specific entities in the in the generated "
                                   "samples (e.g. psychiatric symptoms, disorders, medicines, treatments...). "
                                   "Feel free to add new terms that are not present in the given examples, given "
                                   "they remain plausible for the context of a substance abuse treatment facility."
                                   "Please, do NOT include any of the provided examples above, and make sure to produce"
                                   "samples that are very different from the given ones and from each other.",
        "n_outputs": 2
    },
    {
        "filename": 'seed_diaries_therap.json',
        "description": "therapeutic clinical diary note",
        "additional_instructions": "Please, make sure to use a variety of specific entities in the in the generated "
                                   "samples while maintaining realistic (e.g. substances, people names, locations...). "
                                   "Feel free to invent stories and use imagination. In each generated sample, imagine a"
                                   "different person writing and try to use new terms that are not present in the given "
                                   "examples, given they remain plausible for the context of a report of substance "
                                   "abuse counselling.",
        "n_outputs": 2
    },
    {
        "filename": 'seed_reports.json',
        "description": "therapy report",
        "n_outputs": 2
    }
]
N_PER_OUTPUT = 5            # Number of samples to generate per model output
ENTITIES = [                # Possible NER labels
    {"label": "PATIENT",        "desc": "Names and/or surnames of the patient (e.g. 'Giovanni Verdi', 'Luca')"},
    {"label": "AGE",            "desc": "Person age (e.g. '35 anni', '42enne')"},
    {"label": "PER",            "desc": "Named people other than the patient, like family members, healthcare professionals (e.g. 'Dott.ssa Rossi', 'Mario Bianchi', 'G. Verdi', 'famiglia Visconti')"},
    {"label": "DATE",           "desc": "Dates or absolute time references (e.g. '5 maggio', '2020', '20/03/2021')"},
    {"label": "ORG",            "desc": "Specific organization (e.g. 'SerT di Milano', 'ASL', 'Comunità terapeutica')"},
    {"label": "GPE",            "desc": "Specific geo-political locations (e.g. 'Germania', 'Marche', 'Milano')"},
    {"label": "LOC",            "desc": "Specific non-GPE physical locations or areas (e.g. 'Bar dello Sport', 'via Roma')"},
    {"label": "MISC",           "desc": "Miscellaneous entities, including events, nationalities, products or works of art (e.g. 'Sagra della porchetta', 'messicano', 'X-Factor')"},
    {"label": "SUBSTANCE",      "desc": "Specific substance of abuse (e.g. 'oppioidi', 'cocaina', 'metadone')"},
    {"label": "SYMPTOM",        "desc": "Specific symptom or sign (e.g. 'ansia', 'insonnia', 'dolore addominale')"},
    {"label": "MEDICINE",       "desc": "Specific pharmacological substance (e.g. 'metadone', 'diazepam')"},
    {"label": "DISEASE",        "desc": "Specific disease or disorder (e.g. 'epatite C', 'HIV', 'disturbo d'ansia')"},
    {"label": "EXAMINATION",    "desc": "Specific medical or psychological examination or test (e.g. 'emocromo', 'TAC cerebrale', 'test HIV', 'valproatemia')"},
    {"label": "HEALTH_STATUS",  "desc": "General physical or psychological heath status report (e.g. 'Umore in asse')"},
    {"label": "TREATMENT",      "desc": "General or specific pharmacological or therapeutic treatment (e.g. 'sedazione', 'residenzialità a lungo termine')"}
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
        "label": "string, the NER label for this entity"
      }
    ]
  },
]

Ensure correct JSON syntax, no explanations, and no Markdown code fences.
"""
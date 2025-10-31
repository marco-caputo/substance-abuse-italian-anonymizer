SEED_SAMPLES = [  # Files to use as seed examples
    {
        "filename": 'diaries_psych',
        "description": "psychiatric clinical diary note",
        "additional_instructions": """
                                Please, make sure to use a variety of specific entities in the in the generated
                                   samples (e.g. psychiatric symptoms, disorders, medicines, treatments...).
                                   Feel free to add new terms that are not present in the given examples, given
                                   they remain plausible for the context of a substance abuse treatment facility.
                                   In addition, introduce variability in the entities and structure of each record.
                                    Do not include the same types of information in every entry — for example, some 
                                    records may omit patient data entirely.
                                    Vary the overall layout and phrasing, especially at the beginning of the notes.
                                    Avoid starting all notes with the same pattern and do NOT use the formula 
                                    "<name>, <age>", as provided examples do not do it. Rather, avoid referring explicitly 
                                    to the patient, you can use simply verbs implying the subject.
                                    Each note should have a distinct structure, different ordering of information, 
                                    and variation in which entities appear.
                                    """,
        "n_outputs": 2
    },
    {
        "filename": 'diaries_therap',
        "description": "therapeutic clinical diary note",
        "additional_instructions": """
                                   Please, make sure to use a variety of specific entities in the in the generated
                                   samples while maintaining realistic (e.g. substances, people names, locations...).
                                   Feel free to invent stories and use imagination. In each generated sample, imagine a
                                   different person writing and try to use new terms that are not present in the given
                                   examples, given they remain plausible for the context of a report of substance
                                   abuse counselling. 
                                   In addition, introduce variability in the entities and structure of each record.
                                    Do not include the same types of information in every entry — for example, some 
                                    records may omit patient data entirely.
                                    Vary the overall layout and phrasing, especially at the beginning of the notes.
                                    Avoid starting all notes with the same pattern and do NOT use the formula 
                                    "<name>, <age>", as provided examples do not do it. Rather, avoid referring explicitly 
                                    to the patient, you can use simply verbs implying the subject.
                                    Each note should have a distinct structure, different ordering of information, 
                                    and variation in which entities appear.
                                   """,
        "n_outputs": 2
    },
    {
        "filename": "diaries_it.csv",
        "description": "diary entry in Italian",
        "additional_instructions": """
            Goal:
            Take the examples listed below and insert named entities into each diary entry while keeping the text coherent, 
            realistic, and idiomatic in Italian. Ensure entities are integrated naturally into the narrative and, most 
            importantly, that the diary entries remain plausible and believable.
            
            Strict requirements:
            1. Vary labels: do not use the same subset of labels in every entry; rotate combinations across samples and 
            within entries. Use 2–5 entities per entry, but vary the count.
            2. Diverse examples: when reusing the same label across different entries, use different concrete examples 
            each time.
            3. Coherence: after inserting entities, the diary text must remain natural and plausible in idiomatic Italian.
            4. Faithful spans: every entity span in "entities" must appear verbatim in the "text" and match exactly the 
            intended mention.
            5. Label semantics: respect label meanings (e.g., PATIENT is the patient’s name/surname; PER are other named 
            people; AGE is an age mention like "42 anni"; DATE are explicit dates/time; GPE vs. LOC as defined).
            6. No extra commentary, headers, or code fences.
            7. JSON correctness: valid JSON with double quotes, no trailing commas, and correct arrays/objects.
            """,
        "n_outputs": 10
    }
]
N_PER_OUTPUT = 5            # Number of samples to generate per model output
N_EXAMPLES_PER_PROMPT = 5   # Number of few-shot examples to include in each prompt
ENTITIES = [                # Possible NER labels
    {"label": "PATIENT",        "desc": "Names and/or surnames of the patient"}, # (e.g. 'Giovanni Verdi', 'Luca'),
    {"label": "AGE",            "desc": "Person age"}, #(e.g. '35 anni', '42enne')
    {"label": "PER",            "desc": "Named people other than the patient, like family members, healthcare professionals"}, #(e.g. 'Dott.ssa Rossi', 'Mario Bianchi', 'G. Verdi', 'famiglia Visconti')
    {"label": "DATE",           "desc": "Dates or absolute time references"}, #(e.g. '5 maggio', '2020', '20/03/2021')
    {"label": "ORG",            "desc": "Specific organization"}, #(e.g. 'SerT di Milano', 'ASL', 'Comunità terapeutica')
    {"label": "GPE",            "desc": "Specific geo-political locations"}, #(e.g. 'Germania', 'Marche', 'Milano')
    {"label": "LOC",            "desc": "Specific non-GPE physical locations or areas"}, #(e.g. 'Bar dello Sport', 'via Roma')
    {"label": "MISC",           "desc": "Miscellaneous entities, including events, nationalities, products or works of art"}, #(e.g. 'Sagra della porchetta', 'messicano', 'X-Factor')
    {"label": "SUBSTANCE",      "desc": "Specific substance of abuse"}, #(e.g. 'oppioidi', 'cocaina', 'metadone')
    {"label": "SYMPTOM",        "desc": "Specific symptom or sign"}, #(e.g. 'ansia', 'insonnia', 'dolore addominale')
    {"label": "MEDICINE",       "desc": "Specific pharmacological substance"}, #(e.g. 'metadone', 'diazepam')
    {"label": "DISEASE",        "desc": "Specific disease or disorder"}, #(e.g. 'epatite C', 'HIV', 'disturbo d'ansia')
    {"label": "EXAMINATION",    "desc": "Specific medical or psychological examination or test"}, #(e.g. 'emocromo', 'TAC cerebrale', 'test HIV', 'valproatemia')
    {"label": "HEALTH_STATUS",  "desc": "General physical or psychological heath status report"}, #(e.g. 'Umore in asse')
    {"label": "TREATMENT",      "desc": "General or specific pharmacological or therapeutic treatment"} #(e.g. 'sedazione', 'residenzialità a lungo termine')
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
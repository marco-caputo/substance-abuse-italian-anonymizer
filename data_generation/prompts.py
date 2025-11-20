import json
import random
import re
import sys
from pathlib import Path

from faker import Faker

faker = Faker('it_IT')

# Ensures project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from config import SEED_SAMPLES, ENTITIES_NER, ENTITIES_POST, ENTITIES_EE
from utils import read_json_file

SYSTEM_PROMPT_DIARIES_1 = """
You are tasked with translating English diary entries into Italian, while preserving the same information, meaning and 
style and ensuring natural language use.

Always respond with data samples that follow exactly this format, with no text before or after the JSON:
[
  "first full diary in Italian",
  "second full diary in Italian",
  ...
]

Ensure correct JSON syntax, no explanations, and no Markdown code fences.

"""

SYSTEM_PROMPT_DIARIES_2 = """
You are tasked with generating synthetic training data for a Named Entity Recognition (NER) system that 
processes Italian diary entries with medical and personal content. Your task requires you to take existing diaries, 
insert named entities naturally into the text, ensuring that the entries remain coherent and realistic, and finally 
label all the named entities in the resulting text.

Always respond with data samples that follow exactly this format, with no text before or after the JSON:

[
  {
    "text": "full diary",
    "entities": [
      {
        "text": "string, the entity span from the text",
        "label": "string, the NER label for this entity"
      }
    ]
  }
]

Ensure correct JSON syntax, no explanations, and no Markdown code fences.
"""

SYSTEM_PROMPT_STAFF_DIARIES = """
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

PROMPT_REPORTS_1 = lambda intro, body, outro, docname, name, address, chapters, prob: """
Generate a realistic synthetic Italian therapeutic or clinical reports for substance abuse treatment named \"""" + docname + """\" for the patient """ + name + """ living in """ + address + """

Include different chapters with different headers from the example, describing the clinical situation of the patient for different aspects of the clinical situation, for instance: """ + chapters + """, etc. A conclusive section is not necessary, but possible. Include at most 5 chapters and make it long.
Outside of the introduction, place named entities (e.g. GPEs, dates, named people, organizations, non-GPE physical locations or areas, nationalities...) with """ + prob + """ probability.
Feel free to invent stories and use imagination. 

 Make it in JSON format like the following one. The text can be different from this example in both the structure and type of information. Also pay attention on how the patient is referred throughout the text (like E.), avoiding to use always the same pattern.

{
"text": \"RELAZIONE AI SERVIZI\n""" + intro + """\n\n"""+body+"""\n\n"""+ outro + """\"
}

Imagine a different person writing and try to use new terms that are not present in the given example.
IMPORTANT: Please do NOT include anything else outside of the JSON in your response, no explanations, no text before or after (e.g. NO "Certainly, here is ..."). Moreover, in the "text" field, use just raw text just as I did in the example above, do NOT use Markdown fences or other formatting (e.g. NO ---, ### ...), and do not highlight anything, keep it clean.
"""

PROMPT_REPORTS_2 = lambda report: """
    You have to NER-label a report, and return the list of found entities strictly in JSON format.
    Respond with a single data sample that follow exactly this format, with no text before or after the JSON, no explanations, and no Markdown code fences:

    [
      {
        "text": "string, the entity span from the text",
        "label": "string, the NER label for this entity"
      }
    ]

  Possible entities that can be recognized and listed in the "entities" list are:\n
  """ + "\n".join([f"- {e["label"]}: {e["desc"]} {e["examples"]}" for e in ENTITIES_NER]) + """\n
  """ + "\n".join([f"- {e["label"]}: {e["desc"]} {e["examples"]}" for e in ENTITIES_POST]) + """\n

  While labeling please consider the following instructions:
  - If the patient is mentioned multiple times in different ways (e.g., full name, first name only, initials), each occurrence should be listed as a separate entity in the "entities" list.
  - Avoid overusing labels, use them only when they strictly match the entity. Be precise and conservative. In particular do not use TREATMENT for each line in the list of objectives, rather for the activities. Use HEALTH_STATUS, TREATMENT and MISC labels only when they are perfectly fitting the description.
  - PER should only be used for people names and surnames, please DO NOT USE IT for roles or generic references like "medico", "psichiatra", "madre", "genitori", "famiglia" etc. Only to names like "Mario Rossi", "Dott.ssa Bianchi", "Luca".
  - PATIENT can be applied to abbreviated proper names (e.g., "E.", "G. Verdi").

  Again, please be precise and conservative, do not use too many labels, only when they strictly match the entity.

  Here is the report to label:\n
    """ + report

ADDITIONAL_INSTRUCTIONS = {
    "diaries_psych": """
    Please, make sure to use a variety of specific entities in the in the generated samples (e.g. psychiatric symptoms, disorders, medicines, treatments...). Feel free to add new terms that are not present in the given examples, given they remain plausible for the context of a substance abuse treatment facility. In addition, introduce variability in the entities and structure of each record. Do not include the same types of information in every entry — for example, some records may omit patient data entirely. Vary the overall layout and phrasing, especially at the beginning of the notes. Avoid starting all notes with the same pattern and do NOT use the formula "<name>, <age>", as provided examples do not do it. Rather, avoid referring explicitly to the patient, you can use simply verbs implying the subject. Each note should have a distinct structure, different ordering of information, and variation in which entities appear.
    """,
    "diaries_therap": """
    Please, make sure to use a variety of specific entities in the in the generated samples while maintaining realistic. Feel free to invent stories and use imagination. In each generated sample, imagine a different person writing and try to use new terms that are not present in the given examples, given they remain plausible for the context of a report of substance abuse counselling. In addition, introduce variability in the entities and structure of each record. Do not include the same types of information in every entry — for example, some records may omit patient data entirely. Vary the overall layout and phrasing, especially at the beginning of the notes. Avoid starting all notes with the same pattern and do NOT use the formula "<name>, <age>", as provided examples do not do it. Rather avoid referring directly to the patient: you can use simply verbs implying the subject, or you can use the proper name sometimes. Each note should have a distinct structure, different ordering of information, and variation in which entities appear.
    """,
    "reports": """
    Make sure to use a different structures for introductory sentence, following possible templates for therapeutic or clinical reports (e.g., “Relazione ai Servizi”, “Relazione di Dimissione”, “Relazione d’Ingresso”, etc.), where you can insert identifying and administrative information about a patient. Please, also make sure to use varied names, addresses, italian cities etc. that are not present in the given examples and they are not trivial.
    Then include different chapters IN EACH REPORT (possibly with headers, but do NOT use emojis) describing the clinical situation of the patient for different aspects of the clinical situation, for instance: general assessment, family situation, social situation, treatment plan, risk assessment, psychological assessment, posed objectives, level of achievement of objectives, lists of activities, monitoring plan, emotional state, physical health, psychiatric comorbidities, substance abuse history, legal situation, etc. VERY IMPORTANT: Every generated report should be at least 3 paraphs long and have at least 1000 words.
    Outside of the introduction, place named entities from those listed with a very small probability. Feel free to invent stories and use imagination. In each generated sample, imagine a different person writing and try to use new terms that are not present in the given examples.
    Please stick to these and do NOT introduce completely new label names that are not present in the given list (e.g. do NOT use labels like PERSONA or DATA_DI_NASCITA, but rather PER and DATE!). 
    """,
    "diaries_it": {
        "translation": """
        If an expression is not sound in Italian, modify it to make it idiomatic while keeping the original meaning.
        
        For instance the following diary entry:

            - Yesterday, I really felt the importance of my health. I went on a bit longer hike than usual and was very happy that I could do so. It really made me appreciate my health. With all the news of people dying and the tragedy of the Utah family murder in Mexico, it really made me aware of the importance of my own health and well being.

            Should be transformed into:
            [
                "Ieri ho riscoperto l'importanza della salute. Ho fatto un'escursione un po' più lunga del solito e sono stata molto felice di poterla fare. Mi ha fatto stare bene. Con tutte le notizie di persone che muoiono e la tragedia dell'omicidio della famiglia Utah in Messico, mi ha reso davvero consapevole dell'importanza della mia salute e del mio benessere."
            ]
        """,
        "ner": """
        Goal:
            Take the examples listed below and, if possible, insert named entities into each diary entry while keeping 
            the text coherent, realistic, and idiomatic in Italian. Ensure entities are integrated naturally into the 
            narrative and, most importantly, that the diary entries remain plausible and believable.

            Strict requirements:
            > Vary labels: do not use the same subset of labels in every entry; rotate combinations across samples and 
              within entries.
            > Diverse examples: when reusing the same label across different entries, use different concrete examples 
              each time.
            > Completeness: ensure every mentioned entity that is already in the original text is included in the "entities" list with correct "text" and "label".
            > Coherence: after inserting entities, the diary text must remain natural and plausible in idiomatic Italian.
            > Do not limit to appending entities at the end of given diary note, instead integrate them naturally within the text.
            > If no entities can be naturally inserted, you can leave the text unchanged without adding anything, but still provide an empty "entities" list.

            For instance the following diary entry:

            - Ieri ho riscoperto l'importanza della salute. Ho fatto un'escursione un po' più lunga del solito e sono stata molto felice di poterla fare. Mi ha fatto stare bene. Con tutte le notizie di persone che muoiono e la tragedia dell'omicidio della famiglia Utah in Messico, mi ha reso davvero consapevole dell'importanza della mia salute e del mio benessere.

            Should be transformed into:
            {
                "text": "Ieri ho riscoperto l'importanza della salute. Ho fatto un'escursione po' più lunga del solito nel Parco del Gran Sasso e sono stata molto felice di poterla fare. Mi ha fatto stare bene. Con tutte le notizie di persone che muoiono e la tragedia dell'omicidio della famiglia Utah in Messico, mi ha reso davvero consapevole dell'importanza della mia salute e del mio benessere.",
                "entities": [
                  {
                    "text": "Parco del Gran Sasso",
                    "label": "LOC"
                  },
                  {
                    "text": "Utah",
                    "label": "PER"
                  },
                  {
                    "text": "Messico",
                    "label": "GPE"
                  }
                ]
              }
        
        Please do not add extra formatting or symbols for the introduction of entities, just insert them naturally into the text, and report them in the "entities" list as in the example above.
        """,
        "extra": """The HEALTH_STATUS label should be used for general health status descriptions and not isolated health-related words (e.g., "salute" alone should not be labeled), while SYMPTOM can be used for psychological or physical symptoms mentioned in the text (e.g. "ansia", "insonnia")."""
    }
}

EXCLUDED_LABELS = [ent["label"] for ent in ENTITIES_EE]

def _filter_entities_from_samples(samples: list[dict]) -> list[dict]:
    """Removes entities with labels in excluded_labels from each sample's entities list."""
    for sample in samples:
        sample['entities'] = [ent for ent in sample['entities'] if ent['label'] not in EXCLUDED_LABELS]
    return samples

def get_diaries_translation_prompt(chunk: list[str]):
    return f"""
            {SYSTEM_PROMPT_DIARIES_1}
            Here are the {SEED_SAMPLES[-1]['n_per_output']} diary entries that you should translate from Italian to English:
            \n\n- {"\n\n- ".join(chunk)}\n
            {ADDITIONAL_INSTRUCTIONS["diaries_it"]["translation"]}
            """

def get_diaries_ner_prompt(chunk: list[str]) -> str:
    return f"""
            {SYSTEM_PROMPT_DIARIES_2}
            Here are the {SEED_SAMPLES[-1]['n_per_output']} diary entries that you should modify by inserting named entities:
            \n\n- {"\n\n- ".join(chunk)}\n

            Possible entities that can be included are:\n 
            {"\n".join([f"- {e["label"]}: {e["desc"]}" for e in [e for e in ENTITIES_NER if e['label'] not in {'PATIENT'}]])}
            Ensure each example resembles a realistic {SEED_SAMPLES[-1]['description']}\n
            {ADDITIONAL_INSTRUCTIONS["diaries_it"]["ner"]}
            """

def get_staff_diaries_prompt(samples_file: dict) -> str:
    # Build the few-shot prompt
    seed_examples = read_json_file(f"seed_samples/train/seed_{samples_file['filename']}_train.json")
    seed_examples = _filter_entities_from_samples(seed_examples)
    # Select a random subset of examples
    current_examples_text = json.dumps(
        random.sample(seed_examples, min(len(seed_examples), samples_file['n_examples_per_prompt'])), indent=2)

    return f"""
            {SYSTEM_PROMPT_STAFF_DIARIES}\n
            For instance, this is what you should answer when receiving a request for {len(seed_examples)} samples:\n
            {current_examples_text}\n
            Now generate {samples_file['n_per_output']} new {samples_file['description']} samples about patients 
            in substance abuse treatment. 
            Ensure each example resembles a realistic {samples_file['description']} in Italian as those provided above,
            but don't be afraid to vary the style, content and length of the reports.
            Possible entities that can be included are:\n {"\n".join([f"- {e["label"]}: {e["desc"]}" for e in ENTITIES_NER])}\n\n{ADDITIONAL_INSTRUCTIONS[samples_file['filename']]}
            """

def _clean_street_with_number(address: str) -> str:
    """Keeps the street name and the first number, cuts off everything that comes after."""
    match = re.match(r'^(.*?\d+)', address)
    return match.group(1).strip() if match else address.strip()


def _generate_report_prompt_data():
    """Generates random data for report one-shot prompt generation."""
    seed_examples = read_json_file(f"seed_samples/train/seed_reports_train.json")

    intro = random.choice(read_json_file(f"seed_samples/seed_report_info.json")["intros"])
    body = random.choice(seed_examples)["text"]
    outro = random.choice(["", random.choice(read_json_file(f"seed_samples/seed_report_info.json")["outros"])])
    docname = random.choice(read_json_file(f"seed_samples/seed_report_info.json")["docname"])

    name = re.sub(r'^(?:[A-Za-z]+\.)+\s*', '', faker.name())  # Remove titles
    name = re.sub(r'-.*', '', name)  # Remove anything after hyphen
    chapters = ', '.join(
        random.sample(read_json_file(f"seed_samples/seed_report_info.json")["chapters"], k=random.randint(2, 6)))
    where = f"a street named {_clean_street_with_number(faker.street_address())}, municipality of {faker.city()}"
    prob = random.choice(["less"]*5+["equal"]*3+["more"]*2)
    return intro, body, outro, docname, name, where, chapters, prob

def get_report_text_prompt() -> str:
    return PROMPT_REPORTS_1(*_generate_report_prompt_data())

def get_report_label_prompt(text: str) -> str:
    return PROMPT_REPORTS_2(text)
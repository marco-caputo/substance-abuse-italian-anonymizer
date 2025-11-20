# This module provides the settings and functions to anonymize text using the Presidio library.
from typing import Callable

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider, NerModelConfiguration, SpacyNlpEngine
from presidio_anonymizer import AnonymizerEngine

# Define which model to use
model_config = [{"lang_code": "it", "model_name": "it_core_news_lg"}]

# Define which entities the model returns and how they map to Presidio's
entity_mapping = dict(
    PER="PERSON",
    LOC="LOCATION",
    GPE="LOCATION",
    ORG="ORGANIZATION"
)

ner_model_configuration = NerModelConfiguration(default_score = 0.6, model_to_presidio_entity_mapping=entity_mapping)
spacy_nlp_engine = SpacyNlpEngine(models= model_config, ner_model_configuration=ner_model_configuration)

registry = RecognizerRegistry()
registry.load_predefined_recognizers()

analyzer = AnalyzerEngine(nlp_engine=spacy_nlp_engine)

anonymizer = AnonymizerEngine()

PRESIDIO_LABELS = ["LOCATION", "PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "URL"]
PRESIDIO_LABELS_MAPPED = ["LOC", "PER", "PHONE", "EMAIL", "URL"]


def presidio_analyze(text: str) -> list[dict]:
    """
    Applies Presidio to provide the list of detected labelled spans of text.

    :param text: The input text to analyze.
    :return: A list of detected entities with their labels and positions.
    """
    results = analyzer.analyze(text=text, entities=PRESIDIO_LABELS, language='it')
    results = [ {"start": res.start, "end": res.end, "label": res.entity_type } for res in results ]
    for presidio_label, mapped_label in zip(PRESIDIO_LABELS, PRESIDIO_LABELS_MAPPED):
        for res in results:
            if res["label"] == presidio_label:
                res["label"] = mapped_label
    return results

def presidio_anonymize(text: str) -> str:
    """
    Mock function to simulate Presidio anonymization.
    In practice, this would call the actual Presidio anonymization function.
    For testing, we will just replace entities with [LABEL].
    """
    results = analyzer.analyze(text=text, entities=PRESIDIO_LABELS, language='it')
    text = anonymizer.anonymize(text=text, analyzer_results=results).text

    for presidio_label, mapped_label in zip(PRESIDIO_LABELS, PRESIDIO_LABELS_MAPPED):
        text = text.replace(f"<{presidio_label}>", f"[{mapped_label}]")
    return text

def get_presidio_anonymizer() -> Callable:
    """
    Returns a function that anonymizes text using Presidio.
    """
    return presidio_anonymize
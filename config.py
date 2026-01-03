DEFAULT_NER_MODEL = "NER/models/deployed/deployed_v2.2"
DEFAULT_ENTITIES = ["PATIENT", "PER", "LOC", "ORG", "FAC", "GPE", "PROV", "DATE", "NORP", "CODE", "MAIL", "PHONE", "URL"]
DEFAULT_EXTRA_PER_MATCHING = False

PATIENT_DATA_FIELDS = ["anagrafica", "testi"]
SINGLE_TEXT_FIELDS = ["tipo", "testo"]
PERSONAL_DATA_FORMAT = {
    "nome": "PATIENT",
    "cognome": "PATIENT",
    "nazione_nascita": "GPE",
    "luogo_nascita": "GPE",
    "data_nascita": "DATE",
    "nazione_residenza": "GPE",
    "luogo_residenza": "GPE",
    "prov_residenza": "PROV"
}
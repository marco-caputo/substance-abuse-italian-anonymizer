ENTITIES_NER = [                # Possible NER labels
    {"label": "PATIENT",        "desc": "Names and/or surnames of the patient",                                                 "examples": "(e.g. 'Giovanni Verdi', 'Luca')"},
    {"label": "PER",            "desc": "Named people other than the patient, like family members or healthcare professionals", "examples": "(e.g. 'Rossi', 'Mario Bianchi', 'G. Verdi', 'Visconti')"},
    {"label": "ORG",            "desc": "Named organizations, businesses, shops, bars etc.",                                    "examples": "(e.g. 'SerT di Milano', 'ASL', 'Comunità Terapeutica La Quercia')"},
    {"label": "GPE",            "desc": "Named geo-political locations",                                                        "examples": "(e.g. 'Germania', 'Marche', 'Milano')"},
    {"label": "LOC",            "desc": "Named non-GPE physical, geographical location, area names or addresses",               "examples": "(e.g. 'Parco del Gran Sasso', 'via Roma')"},
    {"label": "FAC",            "desc": "Named facilities, hospitals, buildings, airports, highways, bridges etc.",             "examples": "(e.g. 'Ospedale San Raffaele', 'Ponte di Rialto', 'Aeroporto di Fiumicino')"},
    {"label": "NORP",           "desc": "Nationalities or religious or political groups",                                       "examples": "(e.g. 'tedesco', 'cattolico', 'comunista')"},
    {"label": "AGE",            "desc": "Person age",                                                                           "examples": "(e.g. '35 anni', '42enne')"},
    {"label": "DATE",           "desc": "Dates and other absolute time references",                                             "examples": "(e.g. '5 maggio', '2020', '20/03/2021')"},
    {"label": "EVENT",          "desc": "Named events, celebrations, sports events, hurricanes, battles, wars etc.",            "examples": "(e.g. 'Sagra della Porchetta', 'Natale')"},
    {"label": "WORKS_OF_ART",   "desc": "Titles of books, songs, artworks etc.",                                                "examples": "(e.g. 'La Divina Commedia', 'Breaking Bad')"},
    {"label": "PRODUCT",        "desc": "Named products, vehicles, food brand etc. (not services)",                             "examples": "(e.g. 'iPhone', 'Fiat Panda', 'Pavesini')"}
]

ENTITIES_EE = [
    {"label": "SUBSTANCE",      "desc": "Specific substance of abuse", "examples": "(e.g. 'oppioidi', 'cocaina', 'metadone')"},
    {"label": "SYMPTOM",        "desc": "Specific symptom or sign", "examples": "(e.g. 'ansia', 'insonnia', 'dolore addominale')"},
    {"label": "MEDICINE",       "desc": "Specific pharmacological substance", "examples": "(e.g. 'metadone', 'diazepam')"},
    {"label": "DISEASE",        "desc": "Specific disease or disorder", "examples": "(e.g. 'epatite C', 'HIV', 'disturbo d'ansia')"},
    {"label": "EXAMINATION",    "desc": "Specific medical or psychological examination or test", "examples": "(e.g. 'emocromo', 'TAC cerebrale', 'test HIV', 'valproatemia')"},
    {"label": "HEALTH_STATUS",  "desc": "General physical or psychological heath status report", "examples": "(e.g. 'Umore in asse', 'buona salute generale'"},
    {"label": "TREATMENT",      "desc": "General or specific pharmacological or therapeutic treatment", "examples": "(e.g. 'sedazione', 'residenzialità a lungo termine')"}
]

ENTITIES_POST = [
    {"label": "CODE",          "desc": "Codes like fiscal codes, postal codes, ibans, plates or any other code", "examples": "(e.g. 'RSSMRA85M01H501U', '20123')"},
    {"label": "MAIL",          "desc": "Email addresses", "examples": "(e.g. 'marino.cal89@topmail.it')"},
    {"label": "PHONE",         "desc": "Phone numbers", "examples": "(e.g. '+39 333 1234567', '02 12345678')"},
    {"label": "PROV",          "desc": "Italian provinces", "examples": "(e.g. 'MI', 'RM', 'TO')"},
    {"label": "URL",           "desc": "Websites or URLs", "examples": "(e.g. 'www.example.com', 'https://example.org')"}
]

# Files to use as seed examples
SEED_SAMPLES = [
    {
        "filename": 'diaries_psych',
        "description": "psychiatric clinical diary notes",
        "n_examples_per_prompt": 5,
        "n_outputs": {"train" : 0, "test": 0}
    },
    {
        "filename": 'diaries_therap',
        "description": "therapeutic clinical diary notes",
        "n_examples_per_prompt": 5,
        "n_outputs": {"train" : 0, "test": 0}
    },
    {
        "filename": 'diaries_edu',
        "description": "educational clinical diary notes",
        "n_examples_per_prompt": 5,
        "n_outputs": {"train" : 57, "test": 60}
    },
    {
        "filename": 'reports',
        "description": "long reports of a patient in substance abuse treatment (relazioni ai servizi e monitoraggio PTI)",
        "n_examples_per_prompt": 1,
        "n_outputs": {"train" : 0, "test": 0}
    },
    {
        "filename": "diaries_it",
        "description": "diary entry in Italian",
        "n_examples_per_prompt": 5,
        "n_outputs": {"train": 1475 // 5}
    }
]

SEED_PATH_DIARIES = "seed_samples/original_diaries.csv"
TRAIN_TEST_SPLIT_DIARIES = 0.85  # Proportion of data to use for training vs. testing
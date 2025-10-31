from .gen_config import ENTITIES
from .json_conversions import to_spacy_format

SYNTHETIC_DATA_DIR = "synthetic_samples"
SEED_DATA_DIR = "seed_samples"
DATA_FILENAMES = [samples['filename'] for samples in gen_config.SEED_SAMPLES]

SYNTHETIC_DATA_TRAIN_PATHS = [f"{SYNTHETIC_DATA_DIR}/synthetic_{filename}_train.json" for filename in
                              DATA_FILENAMES]
TEST_DATA_PATHS = [f"{SEED_DATA_DIR}/test/seed_{filename}_test.json" for filename in DATA_FILENAMES]

# Extract NER labels from ENTITIES for anonymization by taking all labels until MISC
NER_LABELS = [ent["label"] for ent in ENTITIES[:ENTITIES.index(next(filter(lambda e: e["label"] == "MISC", ENTITIES)))]]
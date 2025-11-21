from config import ENTITIES_NER, ENTITIES_POST
from data_generation import config as gen_config

SYNTHETIC_DATA_DIR = "synthetic_samples"
SEED_DATA_DIR = "seed_samples"
DATA_FILENAMES = [samples['filename'] for samples in gen_config.SEED_SAMPLES]

SYNTHETIC_DATA_PATHS = lambda test_train: [f"{SYNTHETIC_DATA_DIR}/{test_train}/synthetic_{filename}_{test_train}.json" for filename in DATA_FILENAMES]
SEED_DATA_PATHS = lambda test_train: [f"{SEED_DATA_DIR}/{test_train}/seed_{filename}_{test_train}.json" for filename in DATA_FILENAMES]

NER_LABELS = [ent["label"] for ent in ENTITIES_NER]
POST_LABELS = [ent["label"] for ent in ENTITIES_POST]
ANONYMIZATION_LABELS = NER_LABELS + POST_LABELS
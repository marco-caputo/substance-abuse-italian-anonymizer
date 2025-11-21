import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from data_generation import SYNTHETIC_DATA_PATHS, DATA_FILENAMES, NER_LABELS, SEED_DATA_PATHS, POST_LABELS
from utils import load_data_for_spacy, to_docbin_format, combine_docbins
from utils import train_test_split

DATA_PATH_PREFIX = "./../data_generation/"
TRAIN_VAL_SPLIT = 0.8

if __name__ == '__main__':
    train_docbins = []
    val_docbins = []
    test_docbins = []

    for paths in [SEED_DATA_PATHS, SYNTHETIC_DATA_PATHS]:
        for train_test in ['train', 'test']:
            for file_path, file_name in zip(paths(train_test), DATA_FILENAMES):
                training_data = load_data_for_spacy(f"{DATA_PATH_PREFIX}{file_path}")
                if train_test == 'train':
                    train_split, val_split = train_test_split(training_data, train_size=TRAIN_VAL_SPLIT)
                    train_docbins.append(to_docbin_format(train_split, permitted_labels=set(NER_LABELS)))
                    val_docbins.append(to_docbin_format(val_split, permitted_labels=set(NER_LABELS)))
                else:
                    testing_data = load_data_for_spacy(f"{DATA_PATH_PREFIX}{file_path}")
                    test_docbins.append(to_docbin_format(testing_data, permitted_labels=set(NER_LABELS)))

    combine_docbins(train_docbins).to_disk(f"docbins/train.spacy")
    combine_docbins(val_docbins).to_disk(f"docbins/val.spacy")
    combine_docbins(test_docbins).to_disk(f"docbins/test.spacy")

    print("DocBin files created successfully.")
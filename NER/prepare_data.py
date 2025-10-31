# Make the project root importable
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from NER.docbin_utils import load_training_data, to_docbin_format, combine_docbins
from data_generation import SYNTHETIC_DATA_TRAIN_PATHS, DATA_FILENAMES, NER_LABELS, TEST_DATA_PATHS

TRAIN_VAL_SPLIT = 0.8

if __name__ == '__main__':
    train_docbins = []
    val_docbins = []
    test_docbins = []

    for file_path, file_name in zip(SYNTHETIC_DATA_TRAIN_PATHS, DATA_FILENAMES):
        split_index = int(TRAIN_VAL_SPLIT * len(file_path))
        training_data = load_training_data(f"data_generation/{file_path}")
        train_docbins.append(to_docbin_format(training_data[:split_index], permitted_labels=set(NER_LABELS)))
        val_docbins.append(to_docbin_format(training_data[split_index:], permitted_labels=set(NER_LABELS)))

    for file_path, file_name in zip(TEST_DATA_PATHS, DATA_FILENAMES):
        testing_data = load_training_data(f"data_generation/{file_path}")
        test_docbins.append(to_docbin_format(testing_data, permitted_labels=set(NER_LABELS)))

    combine_docbins(train_docbins).to_disk(f"NER/docbins/train.spacy")
    combine_docbins(val_docbins).to_disk(f"NER/docbins/val.spacy")
    combine_docbins(test_docbins).to_disk(f"NER/docbins/test.spacy")

    print("DocBin files created successfully.")
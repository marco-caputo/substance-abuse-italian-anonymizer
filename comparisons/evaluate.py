import re
from typing import List, Tuple, Dict, Callable

from tqdm import tqdm

from utils import read_json_file, to_spacy_format
from data_generation import DATA_FILENAMES, ANONYMIZATION_LABELS
from anonymizers import get_full_anonymizer
from presidio import get_presidio_anonymizer


def infer_predicted_spans(original: str, anonymized: str) -> List[Tuple[int, int, str]]:
    """
    Given the original text and an anonymized version with markers [LABEL],
    infer which span of original text each marker replaced.

    Returns list of (start, end, label).
    """

    pattern = r"\[([A-Z]+)\]"
    predicted = []

    while True:
        match = re.search(pattern, anonymized)
        if not match:
            break

        label = match.group(1)
        tag_start, tag_end = match.span()

        # Text BEFORE the tag in anonymized text
        before = anonymized[:tag_start]

        #Take the index of the next entity or the end of the string
        stop_index = anonymized.find('[', tag_end)
        stop_index = stop_index if stop_index != -1 else len(anonymized)
        after = anonymized[tag_end:stop_index]

        end_index = original.find(after, tag_start)
        entity_text = original[tag_start:end_index]

        replaced_start = tag_start
        replaced_end = end_index

        # Record predicted entity
        predicted.append((replaced_start, replaced_end, label))

        anonymized = before + entity_text + anonymized[tag_end:]

    return predicted


def compute_metrics(gold: Dict, anonymized_text: str) -> tuple[float, float, float]:
    """
    Compute precision, recall and F1 between:
      - gold spaCy formatted annotations: { "text": ..., "entities": [(start,end,label)] }
      - predicted spans inferred from original_text and anonymized_text alignment

    gold: dict
        { "text": ..., "entities": [(start,end,label), ...] }
    anonymized_text: str
        Text with anonymized entities marked as [LABEL]
    Returns: (precision, recall, f1)
    """

    gold_entities = set(gold["entities"])
    pred_entities = set(infer_predicted_spans(gold["text"], anonymized_text))

    tp = len(gold_entities & pred_entities)
    fp = len(pred_entities - gold_entities)
    fn = len(gold_entities - pred_entities)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return precision, recall, f1

def compute_dataset_metrics_per_label(inferences, labels):
    """
    Compute micro-averaged precision, recall, and F1 per label on the given list of gold-anonymized inferences.

    inferences: list of dicts
        {
            "gold": { "text": ..., "entities": [(start,end,label), ...] },
            "anonymized": "..."
        }

    labels: iterable of label strings (e.g. ["PER", "LOC", "ORG"])
    """

    # Initialize counters for each label
    label_counts = {
        lbl: {"tp": 0, "fp": 0, "fn": 0}
        for lbl in labels
    }

    # Global micro-averaged counts
    total_tp = total_fp = total_fn = 0

    for ex in inferences:
        gold_entities = set(ex["gold"]["entities"])
        pred_entities = set(infer_predicted_spans(ex["gold"]["text"], ex["anonymized"]))

        for lbl in labels:
            # filter only this label
            gold_lbl = {(s, e, l) for (s, e, l) in gold_entities if l == lbl}
            pred_lbl = {(s, e, l) for (s, e, l) in pred_entities if l == lbl}

            tp = len(gold_lbl & pred_lbl)
            fp = len(pred_lbl - gold_lbl)
            fn = len(gold_lbl - pred_lbl)

            label_counts[lbl]["tp"] += tp
            label_counts[lbl]["fp"] += fp
            label_counts[lbl]["fn"] += fn

            # accumulate global
            total_tp += tp
            total_fp += fp
            total_fn += fn

    # Compute final metrics
    results = {}

    for lbl in labels:
        tp = label_counts[lbl]["tp"]
        fp = label_counts[lbl]["fp"]
        fn = label_counts[lbl]["fn"]

        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall    = tp / (tp + fn) if (tp + fn) else 0.0
        f1        = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

        results[lbl] = {
            "precision": precision,
            "recall": recall,
            "f1": f1
        }

    # Add global micro-average
    micro_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0.0
    micro_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 0.0
    micro_f = 2 * micro_p * micro_r / (micro_p + micro_r) if (micro_p + micro_r) else 0.0

    results["micro"] = {
        "precision": micro_p,
        "recall": micro_r,
        "f1": micro_f
    }

    return results

def get_test_data():
    """Returns the full test dataset in spaCy format."""
    test_data = []
    for file_name in DATA_FILENAMES:
        data = read_json_file(f"./../data_generation/seed_samples/test/seed_{file_name}_test.json")
        data = to_spacy_format(data)
        test_data.extend(data)

    return test_data


def evaluate_anonymizer_on_test_set(anonymizer: Callable, test_set):
    """
    Evaluate the given anonymizer on the test set and compute metrics per label.
    The test_set should be in spaCy format: list of (text, {"entities": [...]})

    :param anonymizer: function that takes text and returns anonymized text
    :param test_set: list of (text, {"entities": [...]})
    :return: dict of metrics per label
    """
    inferences = []
    for text, ent_dict in tqdm(test_set, desc="Applying anonymizer"):
        sample = {"text": text, "entities": ent_dict["entities"]}
        inferences.append({"gold": sample, "anonymized": anonymizer(text)})

    return compute_dataset_metrics_per_label(inferences, ANONYMIZATION_LABELS)

if __name__ == "__main__":
    test_set = get_test_data()
    model_path = "../NER/models/fine_tuned/gpu/model2_best/"
    nlp_anonymizer = get_full_anonymizer(model_path)
    presidio_anonymizer = get_presidio_anonymizer()

    print(evaluate_anonymizer_on_test_set(presidio_anonymizer, test_set))



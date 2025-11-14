import re
from typing import List, Tuple, Dict
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from tqdm import tqdm

from utils import read_json_file, to_spacy_format
from data_generation import DATA_FILENAMES, ANONYNIZATION_LABELS
from anonymizers import get_full_anonymizer

# Set up the engine, loads the NLP module (spaCy model by default)
# and other PII recognizers
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()
PRESIDIO_LABELS = ["LOCATION", "PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "URL"]
PRESIDIO_LABELS_MAPPED = ["LOC", "PER", "PHONE", "EMAIL", "URL"]


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


def compute_metrics(gold: Dict, original_text: str, anonymized_text: str):
    """
    Compute precision, recall and F1 between:
      - gold spaCy formatted annotations: { "text": ..., "entities": [(start,end,label)] }
      - predicted spans inferred from original_text ↔ anonymized_text alignment
    """

    gold_entities = set(gold["entities"])
    pred_entities = set(infer_predicted_spans(original_text, anonymized_text))

    tp = len(gold_entities & pred_entities)
    fp = len(pred_entities - gold_entities)
    fn = len(gold_entities - pred_entities)

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return precision, recall, f1

def compute_dataset_metrics_per_label(examples, labels):
    """
    Compute micro-averaged precision, recall, and F1 per label.

    examples: list of dicts
        {
            "gold": { "text": ..., "entities": [(start,end,label), ...] },
            "original": "...",
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

    for ex in examples:
        gold_entities = set(ex["gold"][1]["entities"])
        pred_entities = set(infer_predicted_spans(ex["original"], ex["anonymized"]))

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
    test_data = []
    for file_name in DATA_FILENAMES:
        data = read_json_file(f"./../data_generation/seed_samples/test/seed_{file_name}_test.json")
        data = to_spacy_format(data)
        test_data.extend(data)
    return test_data

def get_presidio_anonymized(text: str) -> str:
    """
    Mock function to simulate Presidio anonymization.
    In practice, this would call the actual Presidio anonymization function.
    For testing, we will just replace entities with [LABEL].
    """
    # Call analyzer to get results
    results = analyzer.analyze(text=text,
                               entities=PRESIDIO_LABELS,
                               language='en')
    text = anonymizer.anonymize(text=text, analyzer_results=results).text
    for presidio_label, mapped_label in zip(PRESIDIO_LABELS, PRESIDIO_LABELS_MAPPED):
        text = text.replace(f"<{presidio_label}>", f"[{mapped_label}]")
    return text

if __name__ == "__main__":
    test_set = get_test_data()
    model_path = "../NER/models/gpu/model2_best/"
    nlp_anonymizer = get_full_anonymizer(model_path)
    test_samples = []

    for samples in tqdm(test_set):
        test_samples.append({"gold": samples, "original": samples[0], "anonymized": nlp_anonymizer(samples[0])})

    print(ANONYNIZATION_LABELS)
    print(compute_dataset_metrics_per_label(test_samples, ANONYNIZATION_LABELS))



import re
from typing import List, Tuple, Dict, Callable

import spacy
from tqdm import tqdm

from utils import read_json_file, to_spacy_format
from data_generation import DATA_FILENAMES, ANONYMIZATION_LABELS
from anonymize import get_full_labeller
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


def compute_metrics_from_text(inferences: list[dict], labels: list[str]):
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
    label_counts = {lbl: {"tp": 0, "fp": 0, "fn": 0} for lbl in labels}

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

def compute_metrics_from_spacy_docs(gold_docs: list[dict], pred_docs, labels):
    """
    Compute per-label and micro-averaged precision/recall/F1 using spaCy Doc objects.

    gold_docs: list[Doc]    -- ground truth in the form { "text": ..., "entities": [(start,end,label), ...] },
    pred_docs: list[Doc]    -- model predictions
    labels: list[str]       -- entity labels to score
    """

    # Initialize counters
    label_counts = {lbl: {"tp": 0, "fp": 0, "fn": 0} for lbl in labels}

    total_tp = total_fp = total_fn = 0

    for gold_doc, pred_doc in zip(gold_docs, pred_docs):

        gold_entities = {(ent[0], ent[1], ent[2]) for ent in gold_doc["entities"]}
        pred_entities = {(ent.start_char, ent.end_char, ent.label_) for ent in pred_doc.ents}

        for lbl in labels:
            gold_lbl = {(s, e, l) for (s, e, l) in gold_entities if l == lbl}
            pred_lbl = {(s, e, l) for (s, e, l) in pred_entities if l == lbl}

            tp = len(gold_lbl & pred_lbl)
            fp = len(pred_lbl - gold_lbl)
            fn = len(gold_lbl - pred_lbl)

            # Temporary--------------------------------------------------------------------------
            false_positives = [(gold_doc['text'][s:e], l) for (s, e, l) in pred_lbl - gold_lbl]
            false_negatives = [(gold_doc['text'][s:e], l) for (s, e, l) in gold_lbl - pred_lbl]

            # Save to a text file
            with open("fp.txt", "a", encoding="utf-8") as f:
                for text, label in false_positives:
                    f.write(f"{label}\t{text}\n")

            with open("fn.txt", "a", encoding="utf-8") as f:
                for text, label in false_negatives:
                    f.write(f"{label}\t{text}\n")
            #-------------------------------------------------------------------------------------

            label_counts[lbl]["tp"] += tp
            label_counts[lbl]["fp"] += fp
            label_counts[lbl]["fn"] += fn

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

    # Micro
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
        data = read_json_file(f"./../data_generation/synthetic_samples/test/synthetic_{file_name}_test.json")
        data = to_spacy_format(data)
        test_data.extend(data)

    return test_data


def evaluate_anonymizer_on_text(anonymizer: Callable, test_set):
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

    return compute_metrics_from_text(inferences, ANONYMIZATION_LABELS)

def evaluate_anonymizer_on_docs(anonymizer: Callable, test_set):
    """
    Evaluate the given anonymizer on the test set and compute metrics per label.
    The test_set should be in spaCy format: list of (text, {"entities": [...]})

    :param anonymizer: function that takes text and returns a spacy Doc object
    :param test_set: list of (text, {"entities": [...]})
    :return: dict of metrics per label
    """

    pred_docs = []
    gold_docs = []

    for text, ent_dict in tqdm(test_set, desc="Applying anonymizer"):
        doc = anonymizer(text)
        pred_docs.append(doc)
        gold_docs.append({"text": text, "entities": ent_dict["entities"]})

    return compute_metrics_from_spacy_docs(gold_docs, pred_docs, ANONYMIZATION_LABELS)

if __name__ == "__main__":
    test_set = get_test_data()

    model_path_1 = "../NER/models/deployed/deployed_v2"
    nlp_anonymizer_1 = get_full_labeller(model_path_1)
    nlp_1 = spacy.load(model_path_1)

    model_path_2 = "../NER/models/deployed/deployed_v2.2"
    nlp_anonymizer_2 = get_full_labeller(model_path_2)
    nlp_2 = spacy.load(model_path_2)

    presidio_anonymizer = get_presidio_anonymizer()

    #print("Model v1:")
    #print(evaluate_anonymizer_on_docs(nlp_anonymizer_1, test_set))
    #print(evaluate_anonymizer_on_docs(nlp_1, test_set))

    #print("Model v2.2 NER:")
    #print(evaluate_anonymizer_on_docs(nlp_2, test_set))

    print("Model v2.2 Full:")
    print(evaluate_anonymizer_on_docs(nlp_anonymizer_2, test_set))

    #print("Presidio:")
    #print(evaluate_anonymizer_on_text(presidio_anonymizer, test_set))



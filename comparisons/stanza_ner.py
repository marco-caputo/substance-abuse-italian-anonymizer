import re
import json
from typing import List, Tuple, Dict, Set
import spacy
from spacy.training import Example
from spacy.scorer import Scorer
from stanza import Pipeline, download as stanza_download
import argparse
import logging

# --- Helpers ---


def get_gold_offsets(
    item: Dict,
    labels_to_consider: Set[str],
    gpe_to_loc: bool = True
) -> Dict:
    text = item["text"]
    entities = item.get("entities", [])
    used_spans: Set[Tuple[int,int]] = set()
    result_entities: List[Tuple[int,int,str]] = []

    for ent in entities:
        ent_text = ent["text"]
        label = ent["label"]

        if label not in labels_to_consider and label != "GPE":
            continue
        if gpe_to_loc and label == "GPE":
            label = "LOC"

        pattern = re.escape(ent_text)
        matches = list(re.finditer(pattern, text))
        chosen_span = None
        for m in matches:
            start, end = m.start(), m.end()
            if (start, end) in used_spans:
                continue
            chosen_span = (start, end)
            break
        if chosen_span is None:
            raise ValueError(f"Could not find occurrence of entity text {ent_text!r} in the text: {text!r}")
        start, end = chosen_span
        used_spans.add((start, end))
        result_entities.append((start, end, label))

    return {"text": text, "entities": result_entities}


def get_stanza_predictions(stanza_pipeline: Pipeline, text: str) -> List[Tuple[int,int,str]]:
    doc = stanza_pipeline(text)
    predictions: List[Tuple[int,int,str]] = []
    for sent in doc.sentences:
        sent_ents = getattr(sent, "ents", [])
        for ent in sent_ents:
            start = getattr(ent, "start_char", None)
            end = getattr(ent, "end_char", None)
            label = getattr(ent, "type", None)
            if start is None or end is None or label is None:
                continue
            predictions.append((start, end, label))
    return predictions


def build_spacy_doc_with_entities(nlp, text: str, entities: List[Tuple[int,int,str]]):
    doc = nlp.make_doc(text)
    spans = []
    for start, end, label in entities:
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span is None:
            raise ValueError(f"Could not align span ({start},{end}) -> {text[start:end]!r}")
        spans.append(span)
    doc.ents = tuple(spans)
    return doc


# --- Main evaluation ---


def evaluate_dataset_with_stanza_on_files(data_paths: List[str], stanza_processors: str = "tokenize,ner", log_items: bool = True):
    stanza_download("it", logging_level="ERROR")
    nlp_stanza = Pipeline("it", processors=stanza_processors)
    nlp_spacy = spacy.blank("it")
    examples: List[Example] = []
    total_skipped = 0
    total_items = 0

    for data_path in data_paths:
        print(f"\n--- Processing file: {data_path} ---")
        with open(data_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        for item_idx, item in enumerate(data, start=1):
            total_items += 1
            try:
                gold = get_gold_offsets(item, labels_to_consider={"PER", "LOC", "ORG"})
            except ValueError as e:
                logging.warning(f"[WARN] File {data_path} - Item {item_idx}: {e}")
                total_skipped += 1
                continue

            pred_spans = get_stanza_predictions(nlp_stanza, gold["text"])

            if log_items:
                print(f"\n=== File {data_path} - Item {item_idx} ===")
                print("TEXT:", gold["text"])
                print("GOLD entities (start,end,label,text):")
                for s,e,lbl in gold["entities"]:
                    print(f"  ({s},{e}) {lbl} -> {gold['text'][s:e]!r}")
                print("STANZA predicted entities (start,end,label,text):")
                for s,e,lbl in pred_spans:
                    span_text = gold["text"][s:e] if 0<=s<e<=len(gold["text"]) else "<invalid-offset>"
                    print(f"  ({s},{e}) {lbl} -> {span_text!r}")

            try:
                gold_doc = build_spacy_doc_with_entities(nlp_spacy, gold["text"], gold["entities"])
                pred_doc = build_spacy_doc_with_entities(nlp_spacy, gold["text"], pred_spans)
            except ValueError as e:
                logging.warning(f"[WARN] File {data_path} - Item {item_idx}: alignment failed: {e}")
                total_skipped += 1
                continue

            examples.append(Example(pred_doc, gold_doc))

    if not examples:
        print("\nNo examples to score (all items skipped).")
        return None

    scorer = Scorer()
    scores = scorer.score(examples)
    return scores


# --- Entry point ---


def main():
    parser = argparse.ArgumentParser(description="Evaluate Stanza NER on one or more JSON files")
    parser.add_argument("--files", nargs="+", required=True, help="List of JSON files to run Stanza NER evaluation on")
    parser.add_argument("--log-items", action="store_true", default=False, help="Log each item to console")
    parser.add_argument("--output", type=str, default=None, help="Path to save output JSON (Spacy format)")
    args = parser.parse_args()

    scores = evaluate_dataset_with_stanza_on_files(args.files, log_items=args.log_items)

    if scores and args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(scores, fh, ensure_ascii=False, indent=2)
        print(f"\nSaved scores to {args.output}")

    if scores:
        print("\n=== Overall scores ===")
        print(json.dumps(scores, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

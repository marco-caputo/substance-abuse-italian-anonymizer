# Substance Abuse Italian Anonymizer

A fine-tuned tool for de-identifying italian documents and diaries from substance abuse therapy facilities. 
This has been developed as part of the Digit-Care project, aimed at creating predictive models to support therapeutic pathways for pathological addictions and assisting 4 Italian substance abuse therapy centers in decision making.


This tool anonymizes Italian text using **spaCy NER** plus **custom rule-based detectors**.
It can run from the **command line** or via a **graphical interface (GUI)**.

## Installation
1. Install Git LFS on your machine. This is needed to pull large trained models files.
```bash
git lfs install
```

2. Clone this repository:
```bash
git clone https://github.com/marco-caputo/substance-abuse-italian-anonymizer.git
```

3. Navigate to the project directory:
```bash
cd substance-abuse-italian-anonymizer
```

4. Install the required packages:
```bash
pip install -r requirements.txt
```
## Command Line Usage

### Basic anonymization

```bash
python anonymize.py --text "Mario Rossi vive a Roma."
```

### Anonymize from file

```bash
python anonymize.py --input-file input.txt
```

### Save output to a specific file

```bash
python anonymize.py --input-file input.txt --output-file anonymized.txt
```

### Choose which entity types to anonymize

```bash
python anonymize.py --text "Mario vive a Roma." --entities "PATIENT" "GPE"
```

### Read from stdin

```bash
echo "Mario vive a Roma." | python anonymize.py
```

---

## GUI Mode

To launch the graphical interface:

```bash
python anonymize.py --gui
```

## Configuration

In the config.py file, you can customize default settings about:
- Which entity types to anonymize
- The spaCy model to use

The full list of availble entity types in the latest anonymization model is described in the following table:

| Entity Type | Description               | Examples                  |
|-------------|---------------------------|---------------------------|
| PATIENT     | Patient names             | 'Giovanni Verdi', 'Luca' |
| PER         | Person names              | 'Rossi', 'Mario Bianchi', 'G. Verdi', 'Visconti' |
| LOC         | Locations                 | 'Parco del Gran Sasso', 'via Roma' |
| ORG         | Organizations             | 'SerT di Milano', 'ASL', 'Comunità Terapeutica La Quercia' |
| FAC         | Facilities                | 'Ospedale San Raffaele', 'Ponte di Rialto', 'Aeroporto di Fiumicino' |
| GPE         | Geopolitical entities     | 'Germania', 'Marche', 'Milano' |
| NORP        | Nationalities/Religious/Political groups | 'tedesco', 'cattolico', 'comunista' |
| AGE         | Person age                | '35 anni', '42enne' |
| DATE        | Dates/Time references     | '5 maggio', '2020', '20/03/2021' |
| EVENT       | Events                    | 'Sagra della Porchetta', 'Natale' |
| WORKS_OF_ART| Titles of works           | 'La Divina Commedia', 'Breaking Bad' |
| PRODUCT     | Products                  | 'iPhone', 'Fiat Panda', 'Pavesini' |
| CODE        | Codes (fiscal, postal, etc.)| 'RSSMRA85M01H501U', '20123' |
| MAIL        | Email addresses           | 'marino.mar89@topmail.it' |
| PHONE       | Phone numbers             | '+39 333 1234567', '02 12345678' |
| PROV        | Italian provinces         | 'MI', 'RM', 'TO' |
| URL         | Websites/URLs             | 'www.example.com', 'https://example.org' |

---

## Model Performance

Here is reported the performance of the anonymization and NER models evaluated on the latest test dataset.

### **Deployed Model v2**  
This model (`deployed_2`) is trained on both pre-trained transformer and NER state-transition model from `it_nerIta_trf` (https://huggingface.co/bullmount/it_nerIta_trf)

### **Full Anonymization (NER + Rules)**

| Label | Precision | Recall | F1 |
|-------|-----------|--------|--------|
| PATIENT | 0.908 | 0.958 | 0.932 |
| PER | 0.736 | 0.967 | 0.836 |
| ORG | 0.742 | 0.746 | 0.744 |
| GPE | 0.826 | 0.869 | 0.847 |
| LOC | 0.773 | 0.727 | 0.750 |
| FAC | 0.609 | 0.571 | 0.589 |
| NORP | 0.714 | 0.500 | 0.588 |
| AGE | 0.800 | 0.774 | 0.787 |
| DATE | 0.846 | 0.911 | 0.877 |
| EVENT | 0.744 | 0.674 | 0.707 |
| WORKS_OF_ART | 0.744 | 0.836 | 0.787 |
| PRODUCT | 0.702 | 0.755 | 0.727 |
| CODE | 1.000 | 0.700 | 0.824 |
| PHONE | 0.235 | 1.000 | 0.381 |
| PROV | 0.773 | 0.756 | 0.764 |
| **micro** | **0.801** | **0.868** | **0.833** |

### **NER**

| Label | Precision | Recall | F1 |
|-------|-----------|--------|--------|
| PATIENT | 0.895 | 0.963 | 0.928 |
| PER | 0.924 | 0.953 | 0.939 |
| ORG | 0.731 | 0.736 | 0.733 |
| GPE | 0.820 | 0.877 | 0.847 |
| LOC | 0.770 | 0.727 | 0.748 |
| FAC | 0.622 | 0.587 | 0.604 |
| NORP | 0.714 | 0.500 | 0.588 |
| AGE | 0.800 | 0.774 | 0.787 |
| DATE | 0.848 | 0.927 | 0.886 |
| EVENT | 0.795 | 0.721 | 0.756 |
| WORKS_OF_ART | 0.714 | 0.822 | 0.764 |
| PRODUCT | 0.702 | 0.755 | 0.727 |
| **micro** | **0.835** | **0.855** | **0.845** |

---

### **Deployed Model v1**  
The previous model (`deployed_1`), trained on pre-trained transformer from `bert-base-italian-xxl-cased` (https://huggingface.co/dbmdz/bert-base-italian-xxl-cased) and a newly initialized state-transition NER module.

### **Full Anonymization (NER + Rules)**

| Label | Precision | Recall | F1 |
|-------|-----------|--------|--------|
| PATIENT | 0.848 | 0.953 | 0.898 |
| PER | 0.751 | 0.896 | 0.817 |
| ORG | 0.243 | 0.365 | 0.292 |
| GPE | 0.791 | 0.611 | 0.689 |
| LOC | 0.594 | 0.706 | 0.645 |
| AGE | 0.541 | 0.532 | 0.537 |
| DATE | 0.818 | 0.934 | 0.873 |
| CODE | 0.875 | 0.700 | 0.778 |
| PHONE | 0.308 | 1.000 | 0.471 |
| PROV | 0.773 | 0.756 | 0.764 |
| **micro** | **0.672** | **0.705** | **0.689** |

### **NER**

| Label | Precision | Recall | F1 |
|-------|-----------|--------|--------|
| PATIENT | 0.842 | 0.952 | 0.894 |
| PER | 0.880 | 0.874 | 0.877 |
| ORG | 0.234 | 0.353 | 0.281 |
| GPE | 0.745 | 0.604 | 0.667 |
| LOC | 0.594 | 0.706 | 0.645 |
| AGE | 0.541 | 0.532 | 0.537 |
| DATE | 0.599 | 0.880 | 0.713 |
| **micro** | **0.647** | **0.677** | **0.661** |

### **Presidio Baseline**  
A simple baseline anonymizer using the **spaCy `it_core_news_lg` model** (https://spacy.io/models/it/).
Presidio supports only a subset of entity types and serves primarily as a basic comparison point.

### **Full Anonymization**

| Label | Precision | Recall | F1 |
|-------|-----------|--------|--------|
| PER | 0.279 | 0.702 | 0.400 |
| LOC | 0.039 | 0.364 | 0.070 |



# Substance Abuse Italian Anonymizer

A fine-tuned tool for de-identifying italian documents and diaries from substance abuse therapy facilities. This has been developed as a project for the Natural Language Processing course at Reykjavík University, held by prof. Stefán Ólafsson.

This tool anonymizes Italian text using **spaCy NER** plus **custom rule-based detectors**.
It can run from the **command line** or via a **graphical interface (GUI)**.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/marco-caputo/substance-abuse-italian-anonymizer.git
```

2. Navigate to the project directory:
```bash
cd substance-abuse-italian-anonymizer
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Configuration

In the config.py file, you can customize:
- Which entity types to anonymize
- The spaCy model to use

The full list of availble entity types is described in the following table:

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

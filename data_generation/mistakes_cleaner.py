import re
from faker import Faker
import random

from utils import to_spacy_format
from __init__ import NER_LABELS, POST_LABELS, ANONYMIZATION_LABELS

Faker.seed(42)
random.seed(42)
faker = Faker('it_IT')

# Common Italian names, surnames, and addresses to be replaced
common_names_male = r"\b(?:Luca|Marco|Matteo|Andrea|Alessandro)\b"
common_names_female = r"\b(?:Maria|Carla|Marta|Martina|Giulia|Lucia)\b"
common_surnames = r"\b(?:Rossi|Verdi|Bianchi|Bellini|Moretti|Rinaldi|Ferraris|Ferrante|Ferrari|Bianchi|Greco|Ferri)\b"
common_addresses = r"\b(?:Via Roma|Via delle Rose|Via del Giglio|Via dei Gigli|Corso Italia|Piazza Garibaldi|Viale Europa|Largo Augusto)\b"
common_municipalities = r"\b(?:Milano|Roma|Napoli|Torino|Palermo|Genova|Bologna|Firenze|Venezia|Verona|Catania|Padova|Trieste)\b"
replacements_list = [
        (common_names_male,     lambda: faker.first_name_male()),
        (common_names_female,   lambda: faker.first_name_female()),
        (common_surnames,       lambda: faker.last_name()),
        (common_addresses,      lambda: re.split(r'[,0-9]', faker.street_address())[0].strip()),
        (common_municipalities, lambda: faker.city())
]

# Regex pattern to match family members and other non-proper names referring to people in Italian
wrong_per_pattern = (
    r"\b(?:\s?(?:"
    r"dottoressa|dottore|dottor|dott\.ssa|dott\.r|dott\.|dr\.ssa|dr\.|dott|"
    r"professoressa|professore|professor|prof\.ssoressa|prof\.ssor|prof\.ssa|prof\.sa|prof\.|"
    r"ingegnere|ingegner|ing\.gnere|ing\.|"
    r"avvocato|avvocata|avv\.cato|avv\.|"
    r"signor.|signor|sig\.ora|sig\.ina|sig\.or|sig\.ra|sig\.r|sig\.|"
    r"suor|padre|don|"
    r"madre|mamma|padre|papà|babbo|"
    r"fratello|sorella|fratelli|sorelle|bambin.|"
    r"zi.|cugin.|nonn.|figli.|figli|nipot.|"
    r"familiar.|parent.|genitor.|famigli.|figur.|matern.|patern.|"
    r"person.|amic.|"
    r"partner|fidanzat.|compagn.|moglie|marito|coniuge|"
    r"psicolog.|psichiatr.|medic.|"
    r"pazient.|terapeut.|infermier.|assistent.|operator.|educator.|tutor|mediator.|mediatrice|responsabil.|"
    r"dietist.|manager|dentist.|dermatolog.|ginecolog.|pediatr.|cardiolog.|neurolog.|radiolog.|chirurg.|nutrizionista|fisioterapista|direttore|"
    r"consulent.|counselor|epatolog.|terapist.|"
    r"team|equipe|"
    r"dio"
    r"))+"
)

following_name_pattern = (
    r"(?:\s[a-zà-ÿ'\-]*)*"                 # non-name terms after the wrong PER term
    r"("                                   # true name starts here
    r"(?:\s+[A-ZÀ-Ý](?:\.[A-ZÀ-Ý])*\."     # initials like L. or M.T.
    r"|"                                   # OR
    r"\s+[A-ZÀ-Ý][a-zà-ÿ'\-]+"             # capitalized word with letters, hyphens, apostrophes
    r")+)"
)

wrong_phone_pattern = r"([xX])\1{2,}|([yY])\2{2,}"
phone_prefix_pattern = r'(tel|fax)\.?:?\s*'

wrong_date_pattern = (
    r'(?:'
    r'oggi|domani|ieri|prossim.|scors.|odiern.|ultim.|passat.|nuov.|\sfa|tra\s|fra\s|inizio|'
    r'giorn.|or.|minut.|'
    r'ser.|mattin.|pomeriggio|notte|mezzogiorno|mezzanotte|'
    r'weekend|fine\s?(?:settimana|mese)|'
    r'settimanale|giornalier.|mensil.|annual.|trimestral.|semestral.|'
    r'trimestre|semestre|bimestre|'
    r'compleann.|anniversar.|festivit.|festa|vacanz.|vacanze|period.'
    r')')
wrong_date_pattern_if_alone = (
    r'(?:'
    r'(?:luned.|marted.|mercoled.|gioved.|venerd.|sabato|domenic(?:a|he))(?:\se\s(?:luned.|marted.|mercoled.|gioved.|venerd.|sabato|domenic(?:a|he)))?|'
    r'gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre|'
    r'estat.|invern.|primaver.|autunn.|'
    r'(?:(?:una?|due|tre|quattro|cinque|sei|sette|otto|nove|dieci|undici|dodici)|(?:prim.|second.|terz.|quart.|quint.|sest.|settim.|ottav.|non.|diecim.|undicesim.|dodicesim.)|([1-9][0-9]*))\s(?:ann.|mes.|settiman.)|'
    r'(?:[0-9][0-9]?(?:\.|:|,|\se\s)[0-9][0-9]?)|'
    r'[0-9][0-9]?'
    r')'
)

wrong_province_codes_pattern = r'\b(?:(?:a|A)l|(?:l|L)(?:e|i|o)|(?:m|M)e|(?:s|S)(?:a|i|o)|(?:t|T)e|(?:v|V)(?:a|i))\b'

email_pattern = r'[a-zA-Z0-9\._%+-]+@[a-zA-Z0-9\.-]+[a-zA-Z]{1,}'

wrong_age_pattern = r'(?:adolescent.|anzian.|giovan.|adult.|bambin.|person.|figli|figl.)'
correct_age_pattern = r'((?:[A-Za-z]*|[0-9]*)\s(?:ann.|mes.))'

org_correct_pattern = r'(?:mturk|amazon|twitch|netflix)'  #Common ORGs that can be written lowercase
org_wrong_pattern = r'(?:[0-9]*)'
org_fac_wrong_prefix = (r'(?:bar|ristorante|supermercato|azienda|falegnameria|stazione|comune|'
                        r'(?:centro|cooperativa|comunità|organizzazione|associazione|clinica|ospedale|ambulatorio)\s'
                        r'(?:diurn.|sociale|dipendenze|psicosociale|psichiatric.|formativ.|medic.|'
                        r'di\sreinserimento|di\sriabilitazione|benessere|culturale|clinic.|neuropsichiatric.|terapeutic.|'
                        r'salute\smentale|di\srecupero|maggiore)|centro|cooperativa|comunità|organizzazione|clinica|'
                        r'ospedale|ambulatorio|ospedale|servizio)')

misc_correct_lowercase_pattern = (r'('
        r'italian.|tedesc.|spagnol.|frances.|messican.|portogues.|inglese.|svizzer.|australian.|american.|'
        r'portoghes.|britannic.|bulgar.|canades.|irlandes.|islandes.|giappones.|cines.|corean.|russ.|arab.|'
        r'turco.|polacc.|olandes.|svedes.|norveges.|danes.|finlandes.|grec.|ungheres.|'
        r'bosniac.|croat.|serb.|slovacc.|sloven.|rumen.|belg.|macedon.|albanes.|rumen.|serb.|croat.|bosniac.|'
        r'giordano.|egizian.|marocchin.|tunisin.|algerin.|bulgar.|ucrain.|ebraic.|'
        r'hindi.|bengales.|urdu.|persian.|vietnamit.|indonesian.|filippin.|nigerian.|african.|'
        r'cineforum'
        r')'
)
misc_incorrect_pattern = r'(?:dio|dsm-5|pti|reddito\sdi\scittadinanza)'


def clean_wrong_per(example: dict) -> dict:
    """
    Cleans entities labelled as 'PER' and 'PATIENT' from a given example that actually refer to professional and
    social titles, family members or other non-proper names referring to people.
    If such an entity is found, it attempts to extract a proper name following the term.

    :param example: the example dictionary with "text" and "entities" fields
    :return: cleaned list of entity dicts
    """
    cleaned_entities = []
    for ent in example['entities']:
        if ent['label'] in {'PER','PATIENT'}:
            if re.search(wrong_per_pattern, ent['text'], re.IGNORECASE):
                # Looks for names after the term
                search = re.search(r"(?i:" + wrong_per_pattern + r")" + following_name_pattern, ent['text'])
                if search:
                    ent['text'] = search.group(1).strip()
                else:
                    continue

        cleaned_entities.append(ent)

    example['entities'] = cleaned_entities
    return example

def clean_phone_numbers(example: dict) -> dict:
    """
    Cleans phone numbers when having 'X' instead of digits and removes 'Tel.:' prefix from PHONE entities.

    :param example: the example dictionary with "text" and "entities" fields
    :return: the cleaned example dictionary
    """

    # Remove 'Tel.:' or 'Fax.:' prefixes from PHONE entities
    for ent in example['entities']:
        if ent['label'] == 'PHONE':
            ent['text'] = re.sub(phone_prefix_pattern, '', ent['text'], flags=re.IGNORECASE).strip()

    # Replaces Xs and Ys in phone numbers with random digits
    match = re.search(wrong_phone_pattern, example['text'])
    while match:
        match_text = match.group(0)
        random_number = ''.join(random.choice('0123456789') for _ in range(len(match_text)))
        example['text'] = re.sub(match_text, random_number, example['text'], count=1)
        for ent in example['entities']:
            if ent['label'] == 'PHONE' and ent['text'].find(match_text) != -1:
                ent['text'] = re.sub(match_text, random_number, ent['text'], count=1)
                break
        match = re.search(wrong_phone_pattern, example['text'])

    return example

def clean_dates(example: dict) -> dict:
    """
    Cleans date entities that do not represent absolute references of dates.

    :param example: the example dictionary with "text" and "entities" fields
    :return: the cleaned example dictionary
    """
    cleaned_entities = []

    for ent in example['entities']:
        if ent['label'] == 'DATE':
            if re.search(wrong_date_pattern, ent['text'], re.IGNORECASE) or \
                re.fullmatch(wrong_date_pattern_if_alone, ent['text'], re.IGNORECASE):
                continue
        cleaned_entities.append(ent)

    example['entities'] = cleaned_entities
    return example


def clean_province_codes(example: dict) -> dict:
    """
    Cleans province code entities that are not encountered as proper province codes but are just two-letter words.
    :param example: the example dictionary with "text" and "entities" fields
    :return: the cleaned example dictionary
    """
    cleaned_entities = []
    for ent in example['entities']:
        if ent['label'] == 'PROV':
            if re.fullmatch(wrong_province_codes_pattern, ent['text']):
                continue
        cleaned_entities.append(ent)

    example['entities'] = cleaned_entities
    return example


def clean_mails_as_names(example: dict) -> dict:
    """
    Cleans entities labelled as 'PER' or 'PATIENT' that are actually taken from email addresses.
    """
    for ent in example['entities']:
        if ent['label'] in {'PER','PATIENT','PROV','ORG'}:
            if str.islower(ent['text']):
                for email in re.findall(email_pattern, example['text']):
                    if email.find(ent['text']) != -1:
                        ent['text'] = email
                        ent['label'] = 'MAIL'
                        break

    return example

def clean_locality(example: dict) -> dict:
    """
    Cleans all those locality of facility entities that are not named but are common words.
    This is done simply by checking if the entity text is in lowercase.

    :param example: the example dictionary with "text" and "entities" fields
    :return: the cleaned example dictionary
    """
    cleaned_entities = []
    for ent in example['entities']:
        if ent['label']  in {'LOC',"FAC"}:
            if str.islower(ent['text']):
                continue
        cleaned_entities.append(ent)

    example['entities'] = cleaned_entities
    return example

def clean_age(example: dict) -> dict:
    """
    Cleans age entities that do not represent proper age references.
    The entities are removed if they match a wrong age pattern and do not match a correct age pattern.
    While, if they match both patterns, only the wrong part is removed.

    :param example: the example dictionary with "text" and "entities" fields
    :return: the cleaned example dictionary
    """
    cleaned_entities = []

    for ent in example['entities']:
        if ent['label'] == 'AGE':
            if re.search(wrong_age_pattern, ent['text'], re.IGNORECASE):
                if not re.search(correct_age_pattern, ent['text'], re.IGNORECASE):
                    continue
                else:
                    ent['text'] = re.search(correct_age_pattern, ent['text'], re.IGNORECASE).group(0)
        cleaned_entities.append(ent)

    example['entities'] = cleaned_entities
    return example

def clean_org(example: dict) -> dict:
    """
    Cleans GPE entities that are not proper names of organizations or that are preceded by the common name of the
    organization.
    Those entities that are fully lowercase and do not fall in the list of common organizations,
    or match common wrong patterns are removed.

    :param example: the example dictionary with "text" and "entities" fields
    :return: the cleaned example dictionary
    """
    cleaned_entities = []
    for ent in example['entities']:
        if ent['label'] == 'ORG':
            if str.islower(ent['text']) and not re.search(org_correct_pattern, ent['text'], re.IGNORECASE):
                continue
            if re.fullmatch(org_wrong_pattern, ent['text']):
                continue
            search = re.search(r".*(?i:" + org_fac_wrong_prefix + r")" + r"\s(.*)", ent['text'])
            if search:
                ent['text'] = search.group(1).strip()
                if re.match(r"di\s.*", ent['text'], re.IGNORECASE):
                    search = re.search(r"di\s(.*)", ent['text'], re.IGNORECASE)
                    ent['text'] = search.group(0).strip()
                    if re.match(r'(?i:viale|via|corso|piazza|largo|strada|rotonda|vicolo|borgo|contrada|località)\s.*', ent['text']):
                        # If only a street name remains, change label to LOC, else GPE
                        ent['label'] = 'LOC'
                    else:
                        ent['label'] = 'GPE'
            search = re.fullmatch(r'[\'\"](.*)[\'\"]', ent['text'])
            if search:
                ent['text'] = search.group(1).strip()

        cleaned_entities.append(ent)

    example['entities'] = cleaned_entities
    return example

def clean_fac(example: dict) -> dict:
    """
    Cleans FAC entities that are preceded by a common name of the facility. If only a gpe remanins, the label of the
    entity is changed to GPE.
    """
    cleaned_entities = []
    for ent in example['entities']:
        if ent['label'] == 'FAC':
            if re.search(org_fac_wrong_prefix, ent['text'], re.IGNORECASE):
                # Removes the common facility name
                if re.fullmatch(org_fac_wrong_prefix, ent['text'], re.IGNORECASE):
                    continue
                search = re.search(r".*(?i:" + org_fac_wrong_prefix + r")\s(.*)", ent['text'])
                if search:
                    ent['text'] = search.group(1).strip()
                    if re.match(r"di\s.*", ent['text'], re.IGNORECASE):
                        search = re.search(r"di\s(.*)", ent['text'], re.IGNORECASE)
                        ent['text'] = search.group(0).strip()
                        if re.match(r'(?i:viale|via|corso|piazza|largo|strada|rotonda|vicolo|borgo|contrada|località)\s.*', ent['text']):
                            # If only a street name remains, change label to LOC, else GPE
                            ent['label'] = 'LOC'
                        else:
                            ent['label'] = 'GPE'

            search = re.fullmatch(r'[\'\"](.*)[\'\"]', ent['text'])
            if search:
                # Extracts text within quotes
                ent['text'] = search.group(1).strip()

        cleaned_entities.append(ent)

    example['entities'] = cleaned_entities
    return example

def clean_norp(example: dict) -> dict:
    """Cleans NORP entities that are references to 'Dio'."""
    cleaned_entities = []
    for ent in example['entities']:
        if ent['label'] == 'NORP':
            if re.fullmatch(r'dio', ent['text'], re.IGNORECASE):
                continue
        cleaned_entities.append(ent)

    example['entities'] = cleaned_entities
    return example

def clean_misc(example: dict) -> dict:
    """
    Cleans events, products and work of art entities that are not proper names.
    Those entities that are full lowercase and are not nationalities are removed. Some special case
    having cased words but being common wrong terms are also removed.
    """
    cleaned_entities = []
    for ent in example['entities']:
        if ent['label'] in {'EVENT','PRODUCT', 'WORK_OF_ART'}:
            if str.islower(ent['text']):
                if re.search(misc_correct_lowercase_pattern, ent['text'], re.IGNORECASE):
                    ent['text'] = re.search(misc_correct_lowercase_pattern, ent['text'], re.IGNORECASE).group(0)
                else:
                    continue
            if not re.search(r'[A-ZÀ-Ýa-z]', ent['text']):
                continue
            if re.fullmatch(misc_incorrect_pattern, ent['text'], re.IGNORECASE):
                continue
        cleaned_entities.append(ent)

    example['entities'] = cleaned_entities
    return example


def clean_labels_in_text(example: dict) -> dict:
    """Cleans labels appearing directly in the text or in entities text."""
    for label in ANONYMIZATION_LABELS:
        if re.search(rf'<{label}>', example['text']):
            example['text'] = re.sub(rf'<{label}>', '', example['text'])

    for label in {"LOC", "FAC", "ORG", "GPE", "PATIENT"}:
        if re.search(rf'\b{label}\b', example['text']):
            example['text'] = re.sub(rf'\b{label}\b', '', example['text'])
            for ent in example['entities']:
                if ent['text'].find(label) != -1:
                    ent['text'] = re.sub(rf'\b{label}\b', '', ent['text'])

    return example


def find_patient_mentions(example: dict) -> dict:
    """
    Finds mentions of the patient in the text that are not labelled as entities. This is because patients that are
    introduced with their full names and later mentioned only with their name or surname are not labelled as entities
    in all the different occurrences.

    :param example: the example dictionary with "text" and "entities" fields
    :return: the corrected example dictionary
    """
    patient_name = None
    patient_surname = None
    patient_fullname = None
    for ent in example['entities']:
        if ent['label'] == 'PATIENT' and ent['text'].count(' ') >= 1:
            patient_fullname = ent['text']
            patient_name = ent['text'].split(' ')[0]
            patient_surname = ent['text'].split(' ')[-1]
            break

    def is_isolated_surname(text, patient_name, patient_surname):
        for match in re.finditer(rf'\b{re.escape(patient_surname)}\b', text):
            start = match.start()
            # Check preceding context
            preceding = text[max(0, start - 20):start]  # Look back 20 chars
            if re.search(rf'({re.escape(patient_name)}|{re.escape(patient_name[0])}\.)\s$', preceding):
                continue  # Skip if preceded by full name or initial
            return True
        return False

    def is_isolated_name(text, patient_name, patient_surname):
        for match in re.finditer(rf'\b{re.escape(patient_name)}\b', text):
            end = match.end()
            following = text[end:end + 20]  # Look ahead 20 characters
            # Skip if followed by full surname or initial-surname formats
            if re.match(rf'\s({re.escape(patient_surname)}|{re.escape(patient_surname[0])}\.)', following):
                continue
            return True
        return False

    if patient_fullname: # Finds isolated mentions of name or surname in the text
        text_label_set = {ent['text'] for ent in example['entities'] if ent['label'] == 'PATIENT'}

        # Mario R.
        if (f"{patient_name} {patient_surname[0]}." not in text_label_set and
                re.search(rf'\b{re.escape(patient_name)}\s{re.escape(patient_surname)[0]}\.\b', example['text'])):
            example['entities'].append({'text': f"{patient_name} {patient_surname[0]}.", 'label': 'PATIENT'})

        # Mario
        if patient_name not in text_label_set and is_isolated_name(example['text'], patient_name, patient_surname):
                example['entities'].append({'text': patient_name, 'label': 'PATIENT'})

        # M. R.
        if (f"{patient_name[0]}. {patient_surname[0]}." not in text_label_set and
                re.search(rf'\b{re.escape(patient_name)[0]}\.\s{re.escape(patient_surname)[0]}\.\b', example['text'])):
            example['entities'].append({'text': f"{patient_name[0]}. {patient_surname[0]}.", 'label': 'PATIENT'})

        # M. Rossi
        if (f"{patient_name[0]}. {patient_surname}" not in text_label_set and
                re.search(rf'\b{re.escape(patient_name)[0]}\.\s{re.escape(patient_surname)}\b', example['text'])):
            example['entities'].append({'text': f"{patient_name[0]}. {patient_surname}", 'label': 'PATIENT'})

        # Rossi
        if patient_surname not in text_label_set and is_isolated_surname(example['text'], patient_name, patient_surname):
            example['entities'].append({'text': patient_surname, 'label': 'PATIENT'})

    return example

def remove_leading_spaces(example: dict) -> dict:
    """
    Removes leading and trailing spaces from entity texts.

    :param example: the example dictionary with "text" and "entities" fields
    :return: the cleaned example dictionary
    """
    for ent in example['entities']:
        ent['text'] = ent['text'].strip()
    return example

def clean_common_mistakes(example: dict) -> dict:
    """
    Cleans common labelling mistakes from the entities in the example. Common mistakes include:
    - Mislabelled family members as persons (PER)
    - Presence of titles in person names (PER)

    :param example: the example dictionary with "text" and "entities" fields
    :return: the cleaned example dictionary
    """
    example = remove_labels_not_in_set(example, ANONYMIZATION_LABELS)
    example = clean_labels_in_text(example)
    example = clean_wrong_per(example)
    example = clean_phone_numbers(example)
    example = clean_dates(example)
    example = clean_province_codes(example)
    example = clean_mails_as_names(example)
    example = clean_locality(example)
    example = clean_org(example)
    example = clean_fac(example)
    example = clean_misc(example)
    example = find_patient_mentions(example)
    example = remove_leading_spaces(example)
    return example

def _replace_common_names_text(text: str) -> tuple[str,list[tuple[str,str]]]:
    replacements = []

    for common_terms, replacement in replacements_list:
        match = re.search(common_terms, text)
        while match:
            common_term = match.group(0)
            fake_term = replacement()
            text = re.sub(rf'\b{re.escape(common_term)}\b', fake_term, text)
            replacements.append((common_term, fake_term))
            match = re.search(common_terms, text)

    return text, replacements

def replace_common_names(example: str|dict) -> str|dict:
    """
    Replaces very common Italian names and addresses in the given text or example dictionary with randomly generated
    ones with Faker.

    :param example: either a text string or an example dictionary with "text" and "entities" fields
    :return: the modified text string or example dictionary
    """
    if isinstance(example, str):
        return _replace_common_names_text(example)[0]
    elif isinstance(example, dict):
        example['text'], replacements = _replace_common_names_text(example['text'])
        for ent in example['entities']:
            for old, new in replacements:
                if re.match(rf".*\b{re.escape(old)}\b.*", ent['text']):
                    ent['text'] = re.sub(rf'\b{re.escape(old)}\b', new, ent['text'])
        return example
    else:
        raise ValueError("Input must be either a string or a dictionary.")


def change_some_entities_to_lowercase(example: dict) -> dict:
    """
    Changes a few entities to lowercase with a small probability to simulate common mistakes.

    :param example: the example dictionary with "text" and "entities" fields
    :return: the modified example dictionary
    """
    for ent in example['entities']:
        if ent['label'] in {'PATIENT','PER','ORG','GPE','LOC','FAC','EVENT','WORKS_OF_ART','PRODUCT'}:
            # Checks if the entity is not a substring of another entity to avoid partial replacements
            is_substring = False
            for ent_2 in example['entities']:
                if ent_2 != ent and ent_2['text'].find(ent['text']) != -1:
                    is_substring = True
                    break
            if not is_substring:
                if (not str.islower(ent['text'])) and (random.random() < 0.03):  # 3% chance to lowercase
                    example['text'] = example['text'].replace(ent["text"], ent['text'].lower())
                    for ent_2 in example['entities']:
                        if ent_2['text'] == ent['text'] and ent_2['label'] == ent['label']:
                            ent_2['text'] = ent['text'].lower()

    return example

def remove_labels_not_in_set(example: dict, valid_labels: set) -> dict:
    """
    Removes entities from the example that do not have labels in the given valid_labels set.

    :param example: the example dictionary with "text" and "entities" fields
    :param valid_labels: set of valid labels to keep
    :return: the cleaned example dictionary
    """
    cleaned_entities = [ent for ent in example['entities'] if ent['label'] in valid_labels]
    example['entities'] = cleaned_entities
    return example


if __name__ == '__main__':
    from utils.json_utils import read_json_file, save_json_file, to_readable_format

    for file_name in ["diaries_therap", "diaries_psych", "reports", "diaries_it"]:
        for path in [f"synthetic_samples/train/synthetic_{file_name}_train.json",
                     f"synthetic_samples/test/synthetic_{file_name}_test.json"]:
            data = read_json_file(path)
            data = [clean_common_mistakes(example) for example in data]
            data = [replace_common_names(example) for example in data]
            data = [change_some_entities_to_lowercase(example) for example in data]
            data = to_spacy_format(data)
            data = to_readable_format(data)
            save_json_file(path, data)


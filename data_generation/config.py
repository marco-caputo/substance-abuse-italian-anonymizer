ENTITIES = [                # Possible NER labels
    {"label": "PATIENT",        "desc": "Names and/or surnames of the patient", "examples": "(e.g. 'Giovanni Verdi', 'Luca')"},
    {"label": "AGE",            "desc": "Person age", "examples": "(e.g. '35 anni', '42enne')"},
    {"label": "PER",            "desc": "Named people other than the patient, like family members, healthcare professionals", "examples": "(e.g. 'Dott.ssa Rossi', 'Mario Bianchi', 'G. Verdi', 'famiglia Visconti')"},
    {"label": "DATE",           "desc": "Dates or absolute time references", "examples": "(e.g. '5 maggio', '2020', '20/03/2021')"},
    {"label": "ORG",            "desc": "Specific organization", "examples": "(e.g. 'SerT di Milano', 'ASL', 'Comunità terapeutica')"},
    {"label": "GPE",            "desc": "Specific geo-political locations", "examples": "(e.g. 'Germania', 'Marche', 'Milano')"},
    {"label": "LOC",            "desc": "Specific non-GPE physical locations or areas", "examples": "(e.g. 'Bar dello Sport', 'via Roma')"},
    {"label": "MISC",           "desc": "Miscellaneous entities, including events, nationalities, products or works of art, job positions", "examples": "(e.g. 'Sagra della porchetta', 'messicano', 'X-Factor', 'magazziniere')"},
    {"label": "SUBSTANCE",      "desc": "Specific substance of abuse", "examples": "(e.g. 'oppioidi', 'cocaina', 'metadone')"},
    {"label": "SYMPTOM",        "desc": "Specific symptom or sign", "examples": "(e.g. 'ansia', 'insonnia', 'dolore addominale')"},
    {"label": "MEDICINE",       "desc": "Specific pharmacological substance", "examples": "(e.g. 'metadone', 'diazepam')"},
    {"label": "DISEASE",        "desc": "Specific disease or disorder", "examples": "(e.g. 'epatite C', 'HIV', 'disturbo d'ansia')"},
    {"label": "EXAMINATION",    "desc": "Specific medical or psychological examination or test", "examples": "(e.g. 'emocromo', 'TAC cerebrale', 'test HIV', 'valproatemia')"},
    {"label": "HEALTH_STATUS",  "desc": "General physical or psychological heath status report", "examples": "(e.g. 'Umore in asse', 'buona salute generale'"},
    {"label": "TREATMENT",      "desc": "General or specific pharmacological or therapeutic treatment", "examples": "(e.g. 'sedazione', 'residenzialità a lungo termine')"}
]

ENTITIES_POST = [
    {"label": "CODE",          "desc": "Codes like fiscal codes, postal codes, ibans, plates or any other code", "examples": "(e.g. 'RSSMRA85M01H501U', '20123')"},
    {"label": "MAIL",          "desc": "Email addresses", "examples": "(e.g. 'marino.cal89@topmail.it')"},
    {"label": "PHONE",         "desc": "Phone numbers", "examples": "(e.g. '+39 333 1234567', '02 12345678')"},
    {"label": "PROV",          "desc": "Italian provinces", "examples": "(e.g. 'MI', 'RM', 'TO')"},
    {"label": "URL",           "desc": "Websites or URLs", "examples": "(e.g. 'www.example.com', 'https://example.org')"}
]

SEED_SAMPLES = [  # Files to use as seed examples
    {
        "filename": 'diaries_psych',
        "description": "psychiatric clinical diary notes",
        "additional_instructions": """
                                Please, make sure to use a variety of specific entities in the in the generated
                                   samples (e.g. psychiatric symptoms, disorders, medicines, treatments...).
                                   Feel free to add new terms that are not present in the given examples, given
                                   they remain plausible for the context of a substance abuse treatment facility.
                                   In addition, introduce variability in the entities and structure of each record.
                                    Do not include the same types of information in every entry — for example, some 
                                    records may omit patient data entirely.
                                    Vary the overall layout and phrasing, especially at the beginning of the notes.
                                    Avoid starting all notes with the same pattern and do NOT use the formula 
                                    "<name>, <age>", as provided examples do not do it. Rather, avoid referring explicitly 
                                    to the patient, you can use simply verbs implying the subject.
                                    Each note should have a distinct structure, different ordering of information, 
                                    and variation in which entities appear.
                                    """,
        "n_per_output": 5,
        "n_examples_per_prompt": 5,
        "n_outputs": 0
    },
    {
        "filename": 'diaries_therap',
        "description": "therapeutic clinical diary notes",
        "additional_instructions": """
                                   Please, make sure to use a variety of specific entities in the in the generated
                                   samples while maintaining realistic (e.g. substances, people names, locations...).
                                   Feel free to invent stories and use imagination. In each generated sample, imagine a
                                   different person writing and try to use new terms that are not present in the given
                                   examples, given they remain plausible for the context of a report of substance
                                   abuse counselling. 
                                   In addition, introduce variability in the entities and structure of each record.
                                    Do not include the same types of information in every entry — for example, some 
                                    records may omit patient data entirely.
                                    Vary the overall layout and phrasing, especially at the beginning of the notes.
                                    Avoid starting all notes with the same pattern and do NOT use the formula 
                                    "<name>, <age>", as provided examples do not do it. Rather, avoid referring explicitly 
                                    to the patient, you can use simply verbs implying the subject.
                                    Each note should have a distinct structure, different ordering of information, 
                                    and variation in which entities appear.
                                   """,
        "n_per_output": 5,
        "n_examples_per_prompt": 5,
        "n_outputs": 0
    },
{
        "filename": 'reports',
        "description": "long reports of a patient in substance abuse treatment (relazioni ai servizi e monitoraggio PTI)",
        "additional_instructions": """
                                   Make sure to use a different structures for introductory sentence, following possible templates for therapeutic or clinical reports (e.g., “Relazione ai Servizi”, “Relazione di Dimissione”, “Relazione d’Ingresso”, etc.), where you can insert identifying and administrative information about a patient. Please, also make sure to use varied names, addresses, italian cities etc. that are not present in the given examples and they are not trivial.
                                   Then include different chapters IN EACH REPORT (possibly with headers, but do NOT use emojis) describing the clinical situation of the patient for different aspects of the clinical situation, for instance: general assessment, family situation, social situation, treatment plan, risk assessment, psychological assessment, posed objectives, level of achievement of objectives, lists of activities, monitoring plan, emotional state, physical health, psychiatric comorbidities, substance abuse history, legal situation, etc. VERY IMPORTANT: Every generated report should be at least 3 paraphs long and have at least 1000 words.
                                   Outside of the introduction, place named entities from those listed with a very small probability.
                                   Feel free to invent stories and use imagination. In each generated sample, imagine a
                                   different person writing and try to use new terms that are not present in the given
                                   examples.
                                   Please stick to these and do NOT introduce completely new label names that are not present in the given list (e.g. do NOT use labels like PERSONA or DATA_DI_NASCITA, but rather PER and DATE!). 
                                   """,
        "n_per_output": 1,
        "n_examples_per_prompt": 1,
        "n_outputs": 466
    },
    {
        "filename": "diaries_it",
        "description": "diary entry in Italian",
        "additional_instructions": """
        Goal:
            Take the examples listed below and, if possible, insert named entities into each diary entry while keeping 
            the text coherent, realistic, and idiomatic in Italian. Ensure entities are integrated naturally into the 
            narrative and, most importantly, that the diary entries remain plausible and believable.

            Strict requirements:
            > Vary labels: do not use the same subset of labels in every entry; rotate combinations across samples and 
              within entries.
            > Diverse examples: when reusing the same label across different entries, use different concrete examples 
              each time.
            > Completeness: ensure every mentioned entity that is already in the original text is included in the "entities" list with correct "text" and "label".
            > Coherence: after inserting entities, the diary text must remain natural and plausible in idiomatic Italian.
            > Do not limit to appending entities at the end of given diary note, instead integrate them naturally within the text.
            > If an expression is not sound in Italian, modify it to make it idiomatic while keeping the original meaning.
            > If no entities can be naturally inserted, you can leave the text unchanged without adding anything, but still provide an empty "entities" list.
            > The HEALTH_STATUS label should be used for general health status descriptions and not isolated health-related words (e.g., "salute" alone should not be labeled), while SYMPTOM can be used for psychological or physical symptoms mentioned in the text (e.g. "ansia", "insonnia").

            For instance the following diary entry:

            - Ieri ho sentito l'importanza della mia salute. Ho fatto un'escursione un po' più lunga del solito e sono stata molto felice di poterla fare. Mi ha fatto apprezzare la mia salute. Con tutte le notizie di persone che muoiono e la tragedia dell'omicidio della famiglia Utah in Messico, mi ha reso davvero consapevole dell'importanza della mia salute e del mio benessere.

            Should be transformed into:
            {
                "text": "Ieri ho riscoperto l'importanza della salute. Ho fatto un'escursione nel Parco del Gran Sasso e sono stata molto felice di poterla fare. Mi ha fatto stare bene. Con tutte le notizie di persone che muoiono e la tragedia dell'omicidio della famiglia Utah in Messico, mi ha reso davvero consapevole dell'importanza della mia salute e del mio benessere.",
                "entities": [
                  {
                    "text": "Parco del Gran Sasso",
                    "label": "LOC"
                  },
                  {
                      "text": "Utah",
                      "label": "PER"
                  },
                  {
                      "text": "Messico",
                      "label": "GPE"
                  }
                ]
              }
        """,
        "n_per_output": 5,
        "n_outputs": 1473 // 5
    }
]

SYSTEM_PROMPT = """
You generate realistic synthetic Italian therapy reports for patients in substance abuse treatment.
Each report is NER-labeled and returned strictly in JSON format.

Always respond with data samples that follow exactly this format, with no text before or after the JSON:

[
  {
    "text": "string, the full therapy report in Italian",
    "entities": [
      {
        "text": "string, the entity span from the text",
        "label": "string, the NER label for this entity"
      }
    ]
  },
]

Ensure correct JSON syntax, no explanations, and no Markdown code fences.
"""

PROMPT_REPORTS_1 = lambda intro, outro, docname, name, address, chapters: """
Generate a realistic synthetic Italian therapeutic or clinical reports for substance abuse treatment named \""""+ docname + """\" for the patient """+ name + """ living in """ + address + """

Include different chapters with different headers from the example, describing the clinical situation of the patient for different aspects of the clinical situation, for instance: """+ chapters + """, etc. A conclusive section is not necessary, but possible. Include at most 5 chapters and make it long.
Outside of the introduction, place named entities (e.g. GPEs, dates, named people including the patient, organizations, non-GPE physical locations or areas...) with a very small probability.
Feel free to invent stories and use imagination. 
 
 Make it in JSON format like the following one. Introduction and ending should be similar, reporting the same type of information (e.g. province, contacts ...), but the rest of the text can be different from this example in both the structure and type of information. Also pay attention on how the patient is referred throughout the text (like E.), avoiding to use always the same pattern.

{
"text": \"RELAZIONE AI SERVIZI\n"""+ intro + """\n\n
ANDAMENTO GENERALE
Allo stato attuale E. appare adeguatamente compensato ed il tono dell'umore é in asse. Il ragazzo ad oggi svolge con impegno e costanza le attività ergoterapiche quotidiane e porta avanti le proprie responsabilità nonostante, permanga una motivazione al programma terapeutico parzialmente estrinseca. Ancora oggi, il ragazzo pur assumendo la terapia come da prescrizione dello psichiatria della struttura, non ha una completa consapevolezza della propria condizione, sia in merito alla psicopatologia che in merito alla propria condizione tossicomanica, né ha introiettato la necessità rispetto all'assunzione della terapia. Permane, difatti, nel ragazzo la volontà di interrompere l'assunzione della terapia al termine del programma terapeutico riabilitativo in quanto egli associa - a causa della scarsa consapevolezza e degli obiettivi ancora basici del progetto terapeutico - il benessere psico-fisico alla necessità di essere scevro da ogni tipologia di terapia farmacologica. E. partecipa, ad ogni modo, ai gruppi terapeutici a cadenza settimanale e accede ai colloqui individuali con la case manager, nonostante, spesso, lo stesso necessiti di essere spronato e mostri diverse difficoltà ad affrontare particolari vissuti emotivi, oltreché emergano diverse difficoltà in merito alla verbalizzazione di una richiesta di aiuto funzionale.

AMBIENTE FAMILIARE
Continuano gli incontri famiglia a cadenza mensile in struttura in presenza della coppia genitoriale e dei fratelli del sig. D'Agostini. Il lavoro continua ad essere strutturato e condotto su tutto il sistema familiare, ancora ad oggi, caratterizzato da “non detti” che inducono tutti i membri, che presentano diverse difficoltà in merito ad una comunicazione assertiva e chiara, a mettere in atto modalità relazionali disfunzionali. I genitori, difatti, mostrano ancora oggi alcune criticità nella gestione del sig. D'Agostini ed, in alcuni frangenti, hanno paura delle reazioni del ragazzo a causa di diverse situazioni occorse in passato, nelle quali il figlio Gianpiero ha avuto reazioni esplosive. Per tale ragione la coppia genitoriale si mostra spesso ambivalente e non sufficientemente chiara con l'ospite (sia in relazione a comunicazioni da dargli che in relazione ad eventi da riferirgli), dando continuità alle modalità già utilizzate in passato - prima dell'ingresso in struttura - e , involontariamente, incrementando il nervosismo e la diffidenza dello stesso nei loro confronti, evitandogli di sperimentare esperienze emotive correttive. Il ragazzo ad oggi mantiene costanti contatti telefonici a cadenza settimanale (previsti dalle regole della struttura) con la famiglia, nonostante abbia mostrato, sin da subito, diverse difficoltà di comunicazione con la stessa soprattutto in relazione ad una verbalizzazione assertiva dei propri vissuti e dei propri stati d'animo. Si continua a svolgere, sia a livello individuale nei colloqui con il case manager, che con la famiglia D'Agostini all'interno degli incontri famiglia, una lenta e graduale psico educazione relativa alla problematica psichiatrica del ragazzo e alla dipendenza patologica da sostanze stupefacenti. L’ospite, infatti, vive ancora oggi la comunità passivamente e tende, talvolta, ad attribuire la responsabilità della propria condizione agli altri (come ad esempio alla famiglia a causa della denuncia subita), senza avere una chiara e piena consapevolezza di quanto ciò che ha compiuto, abbia avuto - e abbia ancora oggi - delle conseguenze e ripercussioni sulla propria vita.

AMBITO IDENTITARIO E SOCIALE
All'ingresso in struttura Emanuele ha avuto diverse difficoltà relative alla convivenza: la condivisione degli spazi e la necessità di adattarsi a una routine comunitaria, difatti, hanno rappresentato per lui un notevole disagio in quanto l'altro da sé e le regole imposte limitavano in qualche modo la proprialibertà di movimento. Tale aspetto, seppur si sia affievolito nel tempo, rappresenta un forte limite e un aspetto fortemente caratterizzante per l'ospite. L'impossibilità da parte dell'ospite di poter fare ciò che vuole, nel momento in cui lo desidera, provocaancora oggi in E. un'inevitabile frustrazione che, in determinati momenti, fa difficoltà a gestire. Nonostante queste criticità iniziali, attualmente E. mostra comunque dei progressivi miglioramenti,sia sul piano comportamentale che relazionale. Ad oggi E. è riuscito a creare con il gruppo dei pari un buon rapporto ed è riuscito a creare per sé unospazio adeguato, nonostante esso sia determinato da attività e rapporti interpersonali prettamentesuperficiali e basati sul gioco e sullo scherno ma che, oggi, gli permettono di tollerare quanto più possibile la propria permanenza nella struttura. Prosegue, inoltre, un lavoro graduale volto ad una maggiore acquisizione della consapevolezzarispetto alla propria condizione identitaria, sociale e psichica ed ai meccanismi disfunzionali che lostesso tende ad attivare in relazione a situazioni differenti. Le difficoltà del ragazzo a mettere in discussione i propri pensieri, modalità e comportamentalidisfunzionali, emerse fin dall'inizio, risultano essere ancora presenti: tale reticenza al cambiamentosembra essere funzionale al mantenimento delle dinamiche preesistenti che lo inducono ad averepensieri erronei e giungere a conclusioni dalle quali fatica a distaccarsi emotivamente. Continua dunque, a livello individuale, un lavoro psicoeducativo emozionale - parallelamenteal lavoro volto alla strutturazione di una rappresentazione integrata di sé - che tenga contodelle contraddizioni psicologiche e degli errori di ragionamento dello stesso, che lo inducono, poi,al funzionamento tossicomanico.L’identità del sé appare, infatti, ancor oggi, frammentata, poco strutturata e per lo più correlata ad unostile di vita tossicomanico. Con E. si sta continuando a svolgere, pertanto, un lavoro in merito alla consapevolizzazione dellapropria condizione, attraverso la valorizzazione delle proprie risorse individuali da mettere in campoa favore di un cambiamento funzionale. I nuclei più problematici e sui quali si sta continuando ad incentrare il lavoro terapeuticoconcernono la difficoltà di gestione dell'impulsività e la canalizzazione della rabbia (anche inriferimento alle figure genitoriali).Tali meccanismi sono presumibilmente attivati da una scarsa capacità di coping rispetto allefrustrazioni e agli stati di disagio psichico ed emotivo. Nel corso dei mesi è emersa, inoltre, una totale carenza degli aspetti emotivi, sia in riferimento alriconoscimento degli stati emotivi che vive, che, soprattutto, in riferimento alla verbalizzazione scevrada giudizio, degli stessi, in quanto E. è trincerato dietro una credenza disfunzionale di genereestremamente rigida esplicitando che "i maschi non possono piangere". Parallelamente a tali aspetti, si sta svolgendo un lavoro volto ad una maggiore consapevolezza deipropri vissuti emotivi e all'incremento di abilità assertive.Rimane costante il lavoro di base svolto con la case manager incentrato sulle regole basilari del viverecomune e su una psico educazione relativa alle regole essenziali , in tal senso, si sta continua un lavorosullo sviluppo fin abilità relazionali e di convivenza.Ai fini di un apprendimento efficace per il ragazzo risulta funzionale la strategia basata sul rinforzopositivo e/o negativo.Per quanto concerne la malattia e la tossicodipendenza permane, tutt'oggi, nel ragazzo unatteggiamento piuttosto ambivalente: se in alcuni momenti del percorso riabilitativo E. manifesta lavolontà di modificare parti di sé, in altri, invece, non si riconosce come un tossicodipendente masemplicemente come un "abusatore" saltuario.La motivazione al trattamento da parte del ragazzo tende, quindi, ad essere piuttosto altalenante:diminuisce quando il lavoro introspettivo e la necessaria messa in atto di modalità comportamentali erelazionali più sane diventano per il ragazzo difficoltose da accettare e gestire a livello emotivo.Per tale ragione si sta continuando a svolgere un lavoro individualizzato con l'ospite al fine diimplementare la consapevolezza rispetto alla propria condizione.Rispetto all'abuso di sostanze (siano esse cannabis o cocaina), utilizzate per compensare carenzeindividuali determinate da difficoltà caratteriali e sociali, E. mostra un atteggiamento superficiale eun'assenza di introiezione, sminuendo le problematiche derivate dal consumo che hanno generato in lui uno scompenso psicopatologico.
Gli obiettivi a breve-medio e lungo termine che ci stiamo attualmente prefiggendo e gli obiettivi da perseguire sono i seguenti:

Psicologici
- Consolidazione della motivazione al trattamento e alla cura
- Consolidazione della consapevolezza delle problematiche tossicologiche e psicopatologiche
- Avviare processo di costruzione legami affettivi funzionali
- Definizione di identità e acquisizione di un ruolo sano
- Miglioramento della gestione dei rapporti interpersonali
- Avviare percorso di sviluppo capacità metacognitive
- Avviare un percorso di introspezione personale che la porti a condividere e rievocare eventi di vita passati
- Prosieguo del percorso di tolleranza alla frustrazione
- Avviare il riconoscimento degli stati emotivi
- Avviare percorso di gestione delle emozioni e degli impulsi

Educativi
- Avviare aumento e sviluppo partecipazione ad attività di gruppo (attività ludico-ricreative e ergo-terapiche), riducendo i momenti di chiusura relazionale.
- Acquisizione della dimensione della quotidianità e dell’ordinarietà
- Avviare la cura dell’ambiente che lo circonda
- Rispetto delle regole che connotano uno stile di vita sano e funzionale

Tossicologici
- Completare la disintossicazione fisica dalle sostanze primarie di dipendenza in ambiente protetto
- Riconoscimento, controllo e gestione del craving
- Avviato processo di elaborazione del pensiero critico
"""+ outro + """\"
}

Imagine a different person writing and try to use new terms that are not present in the given example.
IMPORTANT: Please do NOT include anything else outside of the JSON in your response, no explanations, no text before or after (e.g. NO "Certainly, here is ..."). Moreover, in the "text" field, use just raw text just as I did in the example above, do NOT use Markdown fences or other formatting (e.g. NO ---, ### ...), and do not highlight anything, keep it clean.
"""

PROMPT_REPORTS_2 = lambda report: """
    You have to NER-label a report, and return the list of found entities strictly in JSON format.
    Respond with a single data sample that follow exactly this format, with no text before or after the JSON, no explanations, and no Markdown code fences:
    
    [
      {
        "text": "string, the entity span from the text",
        "label": "string, the NER label for this entity"
      }
    ]
    
  Possible entities that can be recognized and listed in the "entities" list are:\n
  """ + "\n".join([f"- {e["label"]}: {e["desc"]} {e["examples"]}" for e in ENTITIES]) + """\n
  """ + "\n".join([f"- {e["label"]}: {e["desc"]} {e["examples"]}" for e in ENTITIES_POST]) + """\n
  
  While labeling please consider the following instructions:
  - If the patient is mentioned multiple times in different ways (e.g., full name, first name only, initials), each occurrence should be listed as a separate entity in the "entities" list.
  - Avoid overusing labels, use them only when they strictly match the entity. Be precise and conservative. In particular do not use TREATMENT for each line in the list of objectives, rather for the activities. Use HEALTH_STATUS, TREATMENT and MISC labels only when they are perfectly fitting the description.
  - PER should only be used for people names and surnames, please DO NOT USE IT for roles or generic references like "medico", "psichiatra", "madre", "genitori", "famiglia" etc. Only to names like "Mario Rossi", "Dott.ssa Bianchi", "Luca".
  - PATIENT can be applied to abbreviated proper names (e.g., "E.", "G. Verdi").
  
  Again, please be precise and conservative, do not use too many labels, only when they strictly match the entity.
  
  Here is the report to label:\n
    """ + report

SEED_PATH_DIARIES = "seed_samples/translated_data_it.csv"

TRAIN_TEST_SPLIT_DIARIES = 0.99  # Proportion of data to use for training vs. testing

SYSTEM_PROMPT_DIARIES = """
You are tasked with generating synthetic training data for a Named Entity Recognition (NER) system that 
processes Italian diary entries with medical and personal content. Your task requires you to take existing diaries
and insert named entities naturally into the text, ensuring that the entries remain coherent and realistic.

Always respond with data samples that follow exactly this format, with no text before or after the JSON:

[
  {
    "text": "full diary",
    "entities": [
      {
        "text": "string, the entity span from the text",
        "label": "string, the NER label for this entity"
      }
    ]
  }
]

Ensure correct JSON syntax, no explanations, and no Markdown code fences.
"""
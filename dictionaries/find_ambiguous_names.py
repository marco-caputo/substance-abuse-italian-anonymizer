import re, csv

names_file_path = 'dictionaries/nomi_it.txt'
with open(names_file_path, 'r', encoding='utf-8', errors='ignore') as f:
    names_dict = f.read()
names_tokens = names_dict.split('\n')
names_tokens = {n.lower() for n in names_tokens}

italian_words_file_path = 'github_dictionaries/660000_parole_italiane.txt'
with open(italian_words_file_path, 'r', encoding='utf-8', errors='ignore') as f:
    italian_words = f.read()

italian_words_tokens = italian_words.split('\n')
italian_words_tokens = {w.lower() for w in italian_words_tokens}

ambiguous = set()
for name in names_tokens:
    if name in italian_words_tokens:
        ambiguous.add(name)

with open('dictionaries/ambiguous_names.txt', 'w', encoding='utf-8') as text_file:
    for name in sorted(ambiguous):
        text_file.write(f"{name}\n")
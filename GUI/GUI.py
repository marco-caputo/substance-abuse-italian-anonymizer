#!/usr/bin/env python3
"""
Minimal GUI tweaks:
- remove 'examples' column from entity table
- remove title next to banner, give banner more horizontal space
Other logic unchanged.
"""

import sys
import os
import threading
from pathlib import Path
from typing import Iterable

# make project root importable (adjust as in your project)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import spacy
from spacy import Language
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

from config import DEFAULT_NER_MODEL, DEFAULT_ENTITIES, DEFAULT_EXTRA_PER_MATCHING
from data_generation import ANONYMIZATION_LABELS
from utils.anonymization_utils import read_file, anonymize_doc, save_many_texts
from rules.rules import apply_rules

# ----------------------------
#   Anonymization function
# ----------------------------
def anonymize(text: str,
              nlp: Language = None,
              entities: Iterable[str] = None,
              per_matching:bool = None,
              personal_data:dict[str,str] = None) -> str:
    if nlp is None:
        nlp = spacy.load(DEFAULT_NER_MODEL)
    if entities is None:
        entities = DEFAULT_ENTITIES
    if per_matching is None:
        per_matching = DEFAULT_EXTRA_PER_MATCHING

    return anonymize_doc(apply_rules(nlp(text), per_matching, personal_data), entities)


# --------------------
#   Entity metadata
# --------------------
ENTITY_INFO = {
    "PATIENT": "Nomi di pazienti",
    "PER": "Persone (nomi e cognomi)",
    "LOC": "Luoghi (posizioni, vie)",
    "ORG": "Organizzazioni",
    "FAC": "Strutture e impianti",
    "GPE": "Entità geopolitiche (paesi, regioni, città)",
    "NORP": "Nazionalità, gruppi religiosi o politici",
    "AGE": "Età della persona",
    "DATE": "Date e riferimenti temporali",
    "EVENT": "Eventi",
    "WORKS_OF_ART": "Titoli di opere",
    "PRODUCT": "Prodotti",
    "CODE": "Codici (fiscali, postali, ecc.)",
    "MAIL": "Indirizzi e-mail",
    "PHONE": "Numeri di telefono",
    "PROV": "Province italiane (sigle)",
    "URL": "Siti web / URL",
}


class AnonymizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anonimizzatore Digit-Care")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        self.selected_files = []
        self.output_dir = ""

        # --- MAIN PANED WINDOW (RESIZABLE SECTIONS) ---
        main_pane = ttk.PanedWindow(root, orient="horizontal")
        main_pane.pack(fill="both", expand=True)

        # LEFT PANEL (file selection + entities)
        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=3)  # give more weight to left (entity table)

        # RIGHT PANEL (log)
        right_frame = ttk.Frame(main_pane, padding=(0, 10, 0, 0))
        main_pane.add(right_frame, weight=1)

        # --- BANNER (full-width, no title) ---
        banner_frame = ttk.Frame(left_frame, padding=(10, 10, 10, 10))
        banner_frame.pack(fill="x", pady=5)

        banner_path = Path(__file__).parent / "banner.png"

        if banner_path.exists():
            try:
                # Load original image
                self.banner_original = Image.open(banner_path)
                self.banner_photo = ImageTk.PhotoImage(self.banner_original)

                # Create label and pack it (this step was missing)
                self.banner_label = ttk.Label(banner_frame, image=self.banner_photo)
                self.banner_label.pack(fill="x", expand=True)

                # Resize dynamically
                banner_frame.bind("<Configure>", self._resize_banner)

            except Exception:
                # Fallback
                try:
                    self.banner_img = tk.PhotoImage(file=str(banner_path))
                    self.banner_label = tk.Label(banner_frame, image=self.banner_img)
                    self.banner_label.pack(fill="x")
                except Exception:
                    tk.Label(banner_frame, text="[banner.png non caricato]", font=("Arial", 12)).pack(fill="x")
        else:
            tk.Label(banner_frame, text="[banner.png non trovato]", font=("Arial", 12)).pack(fill="x")

        # --- FILE SELECTION FRAME ---
        file_frame = ttk.LabelFrame(left_frame, text="1. Seleziona file o cartella")
        file_frame.pack(fill="x", padx=10, pady=6)

        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Seleziona File", command=self.select_files).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Seleziona Cartella", command=self.select_folder).pack(side="left", padx=5)

        self.file_listbox = tk.Listbox(file_frame, height=4)
        self.file_listbox.pack(fill="x", padx=10, pady=5)

        # --- ENTITY TABLE FRAME (SCROLLABLE) ---
        entity_frame = ttk.LabelFrame(left_frame, text="2. Seleziona entità da anonimizzare")
        entity_frame.pack(fill="both", expand=True, padx=10, pady=6)
        entity_frame.configure(height=200)

        canvas = tk.Canvas(entity_frame, height=200)
        scroll = ttk.Scrollbar(entity_frame, orient="vertical", command=canvas.yview)
        self.entity_inner = ttk.Frame(canvas)

        # --- Enable mouse wheel scrolling ---
        def _on_mousewheel(event):
            # Windows / Linux
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_mousewheel_mac(event):
            # macOS uses different delta
            canvas.yview_scroll(int(-1 * event.delta), "units")

        # Bind depending on platform
        if sys.platform == "darwin":
            canvas.bind_all("<MouseWheel>", _on_mousewheel_mac)
        else:
            canvas.bind_all("<MouseWheel>", _on_mousewheel)


        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        canvas.create_window((0, 0), window=self.entity_inner, anchor="nw")
        self.entity_inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # headings (no examples column)
        ttk.Label(self.entity_inner, text="", width=3).grid(row=0, column=0, padx=4, pady=4)  # checkbox column
        ttk.Label(self.entity_inner, text="Entità", font=(None, 10, "bold")).grid(row=0, column=1, sticky="w", padx=4)
        ttk.Label(self.entity_inner, text="Descrizione", font=(None, 10, "bold")).grid(row=0, column=2, sticky="w", padx=4)

        # Build table of labels + descriptions
        self.entity_vars = {}

        for r, label in enumerate(ANONYMIZATION_LABELS, start=1):
            var = tk.BooleanVar(value=(label in DEFAULT_ENTITIES))
            self.entity_vars[label] = var

            ttk.Checkbutton(self.entity_inner, variable=var).grid(row=r, column=0, sticky="nw", padx=5, pady=6)
            ttk.Label(self.entity_inner, text=label).grid(row=r, column=1, sticky="w", padx=8, pady=6)
            desc = ENTITY_INFO.get(label, "")
            ttk.Label(self.entity_inner, text=desc, wraplength=740, justify="left").grid(row=r, column=2, sticky="w", padx=8, pady=6)

        # --- Dictionary matching checkbox ---
        dictionary_frame = ttk.Frame(left_frame)
        dictionary_frame.pack(fill="x", padx=10, pady=(10, 0))

        self.use_name_dictionary = tk.BooleanVar(value=DEFAULT_EXTRA_PER_MATCHING)

        ttk.Checkbutton(
            dictionary_frame,
            text="Usa dizionario nomi e cognomi per anonimizzazione aggiuntiva",
            variable=self.use_name_dictionary
        ).pack(anchor="w", padx=4, pady=4)

        # --- OUTPUT DIRECTORY FRAME ---
        output_frame = ttk.LabelFrame(left_frame, text="3. Cartella di destinazione")
        output_frame.pack(fill="x", padx=10, pady=6)

        ttk.Button(output_frame, text="Seleziona cartella", command=self.select_output_folder).pack(side="left", padx=5, pady=6)
        self.output_label = ttk.Label(output_frame, text="Nessuna cartella selezionata", foreground="gray")
        self.output_label.pack(side="left", padx=10)

        # --- ACTION BUTTONS ---
        action_frame = ttk.Frame(left_frame)
        action_frame.pack(fill="x", padx=10, pady=8)

        ttk.Button(action_frame, text="Anonimizza Documenti", command=self.anonymize_documents).pack(side="left", padx=10)
        ttk.Button(action_frame, text="Esci", command=root.quit).pack(side="right", padx=10)

        # --- LOG BOX (Right panel) ---
        log_label = ttk.Label(right_frame, text="Log", font=("Arial", 12, "bold"))
        log_label.pack(anchor="w", padx=5, pady=5)

        self.status_box = tk.Text(right_frame, height=20, bg="#f7f7f7")
        self.status_box.pack(fill="both", expand=True, padx=10, pady=10)


    # --------------------------------------------------------------------
    # Utility methods
    # --------------------------------------------------------------------
    def log(self, message):
        self.status_box.insert("end", message + "\n")
        self.status_box.see("end")

    def _resize_banner(self, event):
        """Resize banner image proportionally when frame size changes."""
        if not hasattr(self, "banner_original"):
            return

        new_w = event.width -20
        orig_w, orig_h = self.banner_original.size

        # keep aspect ratio
        ratio = new_w / orig_w
        new_h = int(orig_h * ratio)

        resized = self.banner_original.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.banner_photo = ImageTk.PhotoImage(resized)
        self.banner_label.config(image=self.banner_photo)

    def select_files(self):
        files = filedialog.askopenfilenames(title="Seleziona File", filetypes=[("Documenti", "*.pdf *.docx *.json *.txt")])
        if files:
            self.selected_files = list(files)
            self.file_listbox.delete(0, "end")
            for f in self.selected_files:
                self.file_listbox.insert("end", f)
            self.log(f"Selezionati {len(files)} file.")

    def select_folder(self):
        folder = filedialog.askdirectory(title="Seleziona Cartella")
        if folder:
            self.selected_files = [os.path.join(folder, f) for f in os.listdir(folder)
                                   if f.lower().endswith((".pdf", ".docx", ".json", ".txt"))]
            self.file_listbox.delete(0, "end")
            for f in self.selected_files:
                self.file_listbox.insert("end", f)
            self.log(f"Caricati tutti i documenti da: {folder}")

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Seleziona cartella")
        if folder:
            self.output_dir = folder
            self.output_label.config(text=folder, foreground="black")
            self.log(f"Cartella di output impostata: {folder}")

    # Main anonymization loop
    def anonymize_documents(self):
        # Immediate GUI update
        self.log("Anonimizzazione in corso...")

        # Run heavy work in background
        worker = threading.Thread(target=self._anonymize_worker)
        worker.start()

    # Main anonymization loop
    def _anonymize_worker(self):
        if not self.selected_files:
            self.root.after(0, lambda: messagebox.showwarning("Attenzione", "Seleziona almeno un documento."))
            return
        if not self.output_dir:
            self.root.after(0, lambda: messagebox.showwarning("Attenzione", "Seleziona una cartella di output."))
            return

        selected_entities = [ent for ent, var in self.entity_vars.items() if var.get()]
        if not selected_entities:
            self.root.after(0,
                            lambda: messagebox.showwarning("Attenzione", "Seleziona almeno una categoria di entità."))
            return

        for file_path in self.selected_files:
            try:
                texts, dict = read_file(file_path)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Errore", f"Impossibile leggere {file_path}: {e}"))
                continue

            if all(not text.strip() for text in texts):
                self.root.after(0, lambda f=file_path: self.log(f"Saltato (vuoto): {f}"))
                continue

            anonymized = [anonymize(text, entities=selected_entities, per_matching=self.use_name_dictionary.get(), personal_data=dict)
                          for text in texts]
            out_path = save_many_texts(
                anonymized,
                output_dir=self.output_dir,
                original_filename=file_path
            )

            self.root.after(0, lambda p=out_path: self.log(f"File anonimizzato salvato: {p}"))

        self.root.after(0, lambda: messagebox.showinfo("Fatto", "Anonimizzazione completata con successo!"))
        self.root.after(0, lambda: self.log("Tutti i file sono stati processati con successo."))


# Entry point
def main():
    root = tk.Tk()
    app = AnonymizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

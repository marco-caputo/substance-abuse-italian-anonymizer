# Make the project root importable
import sys
import os
from pathlib import Path
from typing import Iterable

from data_generation import ANONYMIZATION_LABELS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import spacy
from spacy import Language
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from config import DEFAULT_NER_MODEL, DEFAULT_ENTITIES
from utils.anonymization_utils import save_anonymized_text, read_file, anonymize_doc
from rules.rules import apply_rules


def anonymize(text: str, nlp:Language= None, entities:Iterable[str]=None) -> str:
    if nlp is None: nlp = spacy.load(DEFAULT_NER_MODEL)
    if entities is None: entities = DEFAULT_ENTITIES
    return anonymize_doc(apply_rules(nlp(text)), entities)


class AnonymizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Anonymizer")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        self.selected_files = []
        self.output_dir = ""

        # --- FILE SELECTION FRAME ---
        file_frame = ttk.LabelFrame(root, text="1. Select Files or Folder")
        file_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(file_frame, text="Select Files", command=self.select_files).pack(side="left", padx=5, pady=5)
        ttk.Button(file_frame, text="Select Folder", command=self.select_folder).pack(side="left", padx=5, pady=5)

        self.file_listbox = tk.Listbox(file_frame, height=5)
        self.file_listbox.pack(fill="x", padx=10, pady=5)

        # --- ENTITY SELECTION FRAME ---
        entity_frame = ttk.LabelFrame(root, text="2. Select Entities to Anonymize")
        entity_frame.pack(fill="x", padx=10, pady=10)

        self.entity_vars = {label: tk.BooleanVar() for label in ANONYMIZATION_LABELS}

        for i, (label, var) in enumerate(self.entity_vars.items()):
            ttk.Checkbutton(entity_frame, text=label, variable=var).grid(row=0, column=i, padx=5, pady=5)

        # --- OUTPUT DIRECTORY FRAME ---
        output_frame = ttk.LabelFrame(root, text="3. Choose Output Folder")
        output_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(output_frame, text="Select Output Folder", command=self.select_output_folder).pack(side="left", padx=5, pady=5)
        self.output_label = ttk.Label(output_frame, text="No folder selected", foreground="gray")
        self.output_label.pack(side="left", padx=10)

        # --- ACTION BUTTONS ---
        action_frame = ttk.Frame(root)
        action_frame.pack(fill="x", padx=10, pady=20)

        ttk.Button(action_frame, text="Anonymize Documents", command=self.anonymize_documents).pack(side="left", padx=10)
        ttk.Button(action_frame, text="Exit", command=root.quit).pack(side="right", padx=10)

        # --- STATUS TEXT BOX ---
        self.status_box = tk.Text(root, height=10, state="disabled", bg="#f7f7f7")
        self.status_box.pack(fill="both", padx=10, pady=10)

    def log(self, message):
        """Append message to status box."""
        self.status_box.config(state="normal")
        self.status_box.insert("end", message + "\n")
        self.status_box.config(state="disabled")
        self.status_box.see("end")

    def select_files(self):
        files = filedialog.askopenfilenames(title="Select Files", filetypes=[("Documents", "*.pdf *.docx *.txt")])
        if files:
            self.selected_files = list(files)
            self.file_listbox.delete(0, "end")
            for f in self.selected_files:
                self.file_listbox.insert("end", f)
            self.log(f"Selected {len(files)} files.")

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self.selected_files = [os.path.join(folder, f) for f in os.listdir(folder)
                                   if f.lower().endswith((".pdf", ".docx", ".txt"))]
            self.file_listbox.delete(0, "end")
            for f in self.selected_files:
                self.file_listbox.insert("end", f)
            self.log(f"Selected all documents in folder: {folder}")

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_dir = folder
            self.output_label.config(text=folder, foreground="black")
            self.log(f"Output folder set to: {folder}")

    def anonymize_documents(self):
        if not self.selected_files:
            messagebox.showwarning("Warning", "Please select at least one document.")
            return
        if not self.output_dir:
            messagebox.showwarning("Warning", "Please select an output folder.")
            return

        selected_entities = [ent for ent, var in self.entity_vars.items() if var.get()]
        if not selected_entities:
            messagebox.showwarning("Warning", "Please select at least one entity type.")
            return

        self.log("Starting anonymization process...")

        for file_path in self.selected_files:
            text=""
            try:
                text = read_file(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read {file_path}: {e}")
            if not text.strip():
                self.log(f"Skipped (empty): {file_path}")
                continue

            anonymized = anonymize(text, entities=selected_entities)
            out_path = save_anonymized_text(anonymized, output_dir=self.output_dir, original_filename=file_path)
            self.log(f"Saved anonymized file: {out_path}")

        messagebox.showinfo("Done", "Anonymization completed successfully!")
        self.log("All files processed successfully.")


def main():
    root = tk.Tk()
    app = AnonymizerApp(root)
    root.mainloop()

# ---------- RUN APP ----------
if __name__ == "__main__":
    main()

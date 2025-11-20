# Make the project root importable
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import spacy
from docx import Document
from PyPDF2 import PdfReader

# Load spaCy English model
nlp = spacy.load("it_core_news_trf")


# ---------- HELPER FUNCTIONS ----------

def read_file(file_path):
    """Reads a file and returns its text content."""
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        elif ext == ".docx":
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif ext == ".pdf":
            reader = PdfReader(file_path)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
        else:
            raise ValueError("Unsupported file type.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read {file_path}: {e}")
    return text


def anonymize_text(text, entities_to_anonymize):
    """Replaces selected entity types with anonymized placeholders."""
    doc = nlp(text)
    anonymized = text
    offset = 0

    for ent in doc.ents:
        if ent.label_ in entities_to_anonymize:
            start, end = ent.start_char + offset, ent.end_char + offset
            replacement = f"[{ent.label_}]"
            anonymized = anonymized[:start] + replacement + anonymized[end:]
            offset += len(replacement) - (end - start)

    return anonymized


def save_anonymized_text(output_dir, filename, text):
    """Saves anonymized text to a .txt file."""
    base_name = os.path.splitext(os.path.basename(filename))[0]
    out_path = os.path.join(output_dir, f"{base_name}_anonymized.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    return out_path


# ---------- MAIN APPLICATION ----------

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

        self.entity_vars = {
            "PERSON": tk.BooleanVar(),
            "ORG": tk.BooleanVar(),
            "GPE": tk.BooleanVar(),
            "LOC": tk.BooleanVar(),
            "DATE": tk.BooleanVar(),
            "EMAIL": tk.BooleanVar(),
        }

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
            text = read_file(file_path)
            if not text.strip():
                self.log(f"Skipped (empty): {file_path}")
                continue

            anonymized = anonymize_text(text, selected_entities)
            out_path = save_anonymized_text(self.output_dir, file_path, anonymized)
            self.log(f"Saved anonymized file: {out_path}")

        messagebox.showinfo("Done", "Anonymization completed successfully!")
        self.log("All files processed successfully.")


# ---------- RUN APP ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = AnonymizerApp(root)
    root.mainloop()

import fitz
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def merge_pdfs():
    root = tk.Tk()
    root.withdraw()

    file_paths = filedialog.askopenfilenames(
        title="Select PDF Lectures to Combine",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not file_paths:
        return

    output_path = filedialog.asksaveasfilename(
        title="Save Combined PDF As",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not output_path:
        return

    try:
        combined_pdf = fitz.open()

        for path in file_paths:
            with fitz.open(path) as current_pdf:
                combined_pdf.insert_pdf(current_pdf)

        combined_pdf.save(output_path)
        combined_pdf.close()

        messagebox.showinfo(
            "Success", 
            f"Successfully merged {len(file_paths)} files!\n\nSaved as:\n{os.path.basename(output_path)}"
        )

    except Exception as e:
        messagebox.showerror("Error", f"Failed to merge.\n\nDetails: {e}")

if __name__ == "__main__":
    merge_pdfs()
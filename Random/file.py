import win32com.client
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_to_pdf():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select Word / PowerPoint Document to Convert",
        filetypes=[
            ("All Office Files", "*.docx *.doc *.pptx *.ppt"),
            ("Word files", "*.docx *.doc"),
            ("PowerPoint files", "*.pptx *.ppt")
        ]
    )

    if not file_path:
        return

    file_path = os.path.abspath(file_path)
    file_name = os.path.basename(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    base_path = os.path.splitext(file_path)[0]
    pdf_path = base_path + ".pdf"

    if os.path.exists(pdf_path):
        try:
            with open(pdf_path, 'a'):
                pass
        except IOError:
            messagebox.showerror("Error", "The PDF is currently open in another program. Please close it and try again.")
            return

    app = None
    try:
        if ext in ['.docx', '.doc']:
            try:
                app = win32com.client.GetActiveObject("Word.Application")
            except:
                app = win32com.client.Dispatch("Word.Application")
            
            print(f"Opening Word: {file_name}")
            doc = app.Documents.Open(file_path, ReadOnly=True, Visible=False)
            doc.ExportAsFixedFormat(pdf_path, ExportFormat=17)
            doc.Close(SaveChanges=0)
            
            if app.Documents.Count == 0:
                app.Quit()

        elif ext in ['.pptx', '.ppt']:
            try:
                app = win32com.client.GetActiveObject("PowerPoint.Application")
            except:
                app = win32com.client.Dispatch("PowerPoint.Application")
            
            print(f"Opening PowerPoint: {file_name}")
            pres = app.Presentations.Open(file_path, ReadOnly=True, WithWindow=False)
            pres.SaveAs(pdf_path, FileFormat=32)
            pres.Close()
            
            if app.Presentations.Count == 0:
                app.Quit()
        
        messagebox.showinfo(
            "Success", 
            f"Successfully converted:\n{file_name}\n\nSaved as:\n{os.path.basename(pdf_path)}"
        )

    except Exception as e:
        messagebox.showerror("Error", f"Failed to convert.\n\nDetails: {e}")

if __name__ == "__main__":
    convert_to_pdf()
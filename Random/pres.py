import win32com.client
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_ppt_to_pdf():
    root = tk.Tk()
    root.withdraw()

    ppt_path = filedialog.askopenfilename(
        title="Select PowerPoint File",
        filetypes=[("PowerPoint files", "*.pptx *.ppt")]
    )

    if not ppt_path:
        return

    ppt_path = os.path.abspath(ppt_path)
    base_path = os.path.splitext(ppt_path)[0]
    pdf_path = base_path + ".pdf"

    if os.path.exists(pdf_path):
        try:
            with open(pdf_path, 'a'):
                pass
        except IOError:
            messagebox.showerror("Error", f"The PDF is currently open in another program. Please close it and try again.")
            return

    ppt_app = None
    try:
        ppt_app = win32com.client.GetActiveObject("PowerPoint.Application")
    except:
        ppt_app = win32com.client.Dispatch("PowerPoint.Application")

    try:
        print(f"Opening: {ppt_path}")
        presentation = ppt_app.Presentations.Open(ppt_path, ReadOnly=True, WithWindow=False)
        
        print(f"Saving to: {pdf_path}")
        presentation.SaveAs(pdf_path, FileFormat=32)
        presentation.Close()
        
        messagebox.showinfo("Success", "Conversion complete!")

    except Exception as e:
        messagebox.showerror("COM Error", f"Failed to convert.\n\nDetails: {e}")
    
    finally:
        if ppt_app:
            if ppt_app.Presentations.Count == 0:
                ppt_app.Quit()

if __name__ == "__main__":
    convert_ppt_to_pdf()
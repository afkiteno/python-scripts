import win32com.client

def convert_ppt_to_pdf(ppt_path, pdf_path):
    ppt_app = win32com.client.Dispatch("PowerPoint.Application")
    presentation = ppt_app.Presentations.Open(ppt_path)
    presentation.SaveAs(pdf_path, FileFormat=32)
    presentation.Close()
    ppt_app.Quit()

ppt_path = r''
pdf_path = r''

convert_ppt_to_pdf(ppt_path, pdf_path)
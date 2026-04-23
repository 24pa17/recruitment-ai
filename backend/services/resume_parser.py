import fitz  # PyMuPDF
import docx


def extract_text(file):
    filename = file.filename.lower()

    # 🔹 PDF
    if filename.endswith(".pdf"):
        text = ""
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        for page in pdf:
            text += page.get_text()
        return text

    # 🔹 DOCX
    elif filename.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])

    return ""
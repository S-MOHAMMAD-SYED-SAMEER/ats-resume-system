import pdfplumber
import docx

def extract_text(file):

    if file.type == "application/pdf":

        text=""

        with pdfplumber.open(file) as pdf:

            for page in pdf.pages:

                t = page.extract_text()

                if t:
                    text += t

        return text.lower()

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":

        doc = docx.Document(file)

        text=""

        for p in doc.paragraphs:
            text += p.text+"\n"

        return text.lower()

    return ""
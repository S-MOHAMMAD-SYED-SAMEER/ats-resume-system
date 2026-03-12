from fpdf import FPDF
from PyPDF2 import PdfMerger


def create_candidate_report(df):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial","B",16)

    pdf.cell(0,10,"Shortlisted Candidates",ln=True)

    pdf.set_font("Arial","",12)

    for _,row in df.iterrows():

        pdf.cell(0,8,f"Candidate ID: {row['Candidate ID']}",ln=True)
        pdf.cell(0,8,f"Name: {row['Candidate Name']}",ln=True)
        pdf.cell(0,8,f"Email: {row['Email']}",ln=True)
        pdf.cell(0,8,f"Phone: {row['Phone']}",ln=True)
        pdf.cell(0,8,f"Experience: {row['Experience']}",ln=True)

        pdf.ln(5)

    filename="shortlisted_candidates.pdf"

    pdf.output(filename)

    return filename


def create_resume_list(files):

    merger = PdfMerger()

    for f in files:
        merger.append(f)

    filename="shortlisted_resumes.pdf"

    merger.write(filename)

    merger.close()

    return filename
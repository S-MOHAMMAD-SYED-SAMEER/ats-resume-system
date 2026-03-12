import streamlit as st
import json
import re
import pandas as pd
import pdfplumber
import docx
import os
from fpdf import FPDF
from PyPDF2 import PdfMerger

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="ATS Resume Screening", layout="wide")

# ---------------- USERS ----------------

def load_users():
    with open("users.json") as f:
        return json.load(f)

users = load_users()

# ---------------- LOGIN ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("ATS Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username in users and users[username]["password"] == password:

            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.role = users[username]["role"]

            st.rerun()

        else:
            st.error("Invalid login")

    st.stop()

# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.write("Logged in as:", st.session_state.user)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # ---------------- LOGO SETTINGS ----------------

    st.markdown("### Organization Logo")

    show_logo = st.checkbox("Show Logo", value=True)

    logo_upload = st.file_uploader(
        "Change Organization Logo",
        type=["png","jpg","jpeg"]
    )

    if logo_upload:

        with open("logo/client_logo.jpeg","wb") as f:
            f.write(logo_upload.getbuffer())

        st.success("Logo Updated")

# ---------------- ADMIN PANEL ----------------

if st.session_state.role == "admin":

    st.sidebar.markdown("## User Management")

    users = load_users()

    user_list = list(users.keys())

    selected_user = st.sidebar.selectbox("Select User", user_list)

    # Change Password
    new_password = st.sidebar.text_input("New Password")

    if st.sidebar.button("Update Password"):

        users[selected_user]["password"] = new_password

        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)

        st.sidebar.success("Password Updated")

    # Change Username
    new_username = st.sidebar.text_input("New Username")

    if st.sidebar.button("Change Username"):

        if new_username not in users:

            users[new_username] = users.pop(selected_user)

            with open("users.json", "w") as f:
                json.dump(users, f, indent=4)

            st.sidebar.success("Username Updated")

        else:
            st.sidebar.error("Username already exists")

    # Add User
    st.sidebar.markdown("### Add New User")

    add_user = st.sidebar.text_input("Username ")
    add_pass = st.sidebar.text_input("Password ", type="password")

    role = st.sidebar.selectbox("Role", ["recruiter","admin"])

    if st.sidebar.button("Add User"):

        if add_user not in users:

            users[add_user] = {
                "name": add_user,
                "password": add_pass,
                "role": role
            }

            with open("users.json","w") as f:
                json.dump(users,f,indent=4)

            st.sidebar.success("User Added")

        else:
            st.sidebar.error("User already exists")

    # Delete User
    if st.sidebar.button("Delete User"):

        if selected_user != "admin":

            del users[selected_user]

            with open("users.json","w") as f:
                json.dump(users,f,indent=4)

            st.sidebar.success("User Deleted")

# ---------------- HEADER ----------------

logo_path = "logo/client_logo.jpeg"

if show_logo and os.path.exists(logo_path):

    col1,col2 = st.columns([1,6])

    with col1:
        st.image(logo_path,width=120)

    with col2:
        st.markdown("""
        ## Positive Childhood Alliance North California
        ### AI ATS Resume Screening Dashboard
        """)

else:

    st.markdown("""
    ## Positive Childhood Alliance North California
    ### AI ATS Resume Screening Dashboard
    """)

# ---------------- INPUT ----------------

job_description = st.text_area("Paste Job Description")

uploaded_files = st.file_uploader(
    "Upload Resume Files",
    type=["pdf","docx"],
    accept_multiple_files=True
)

threshold = st.slider("Shortlist Threshold (%)",0,100,60)

# ---------------- TEXT EXTRACTION ----------------

def extract_text(file):

    text = ""

    if file.type == "application/pdf":

        with pdfplumber.open(file) as pdf:

            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":

        doc = docx.Document(file)

        for p in doc.paragraphs:
            text += p.text

    return text.lower()

# ---------------- INFO EXTRACTION ----------------

def extract_email(text):

    email = re.findall(r'\S+@\S+',text)

    return email[0] if email else "Not detected"


def extract_phone(text):

    phone = re.findall(r'\+?\d[\d\s\-]{8,15}',text)

    return phone[0] if phone else "Not detected"


def extract_name(text):

    lines = text.split("\n")

    for line in lines[:5]:

        if len(line.split()) >= 2:
            return line.title()

    return "Not detected"


def extract_experience(text):

    exp = re.findall(r'\d+\+?\s*years?',text)

    return exp[0] if exp else "Not detected"

# ---------------- SKILL MATCHING ----------------

STOPWORDS = {
"the","and","with","for","from","this","that","have","will",
"using","used","skills","skill","work","working","experience"
}

def clean_words(text):

    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

    words = [w for w in words if w not in STOPWORDS and len(w) > 3]

    return words


def analyze_resume(resume_text,job_description):

    docs = [job_description,resume_text]

    vectorizer = TfidfVectorizer()

    tfidf = vectorizer.fit_transform(docs)

    similarity = cosine_similarity(tfidf[0:1],tfidf[1:2])

    score = int(similarity[0][0]*100)

    jd_words = set(clean_words(job_description))
    resume_words = set(clean_words(resume_text))

    matched = list(jd_words.intersection(resume_words))[:10]

    return score,matched

# ---------------- REPORT ----------------

def create_candidate_report(df):

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial",size=12)

    for _,row in df.iterrows():

        pdf.cell(0,10,f"{row['Candidate Name']} | {row['Email']} | {row['Phone']}",ln=True)

    file="shortlisted_candidates.pdf"

    pdf.output(file)

    return file

# ---------------- MERGE RESUMES ----------------

def merge_resumes(files):

    merger = PdfMerger()

    for f in files:
        merger.append(f)

    file="shortlisted_resumes.pdf"

    merger.write(file)
    merger.close()

    return file

# ---------------- ANALYZE ----------------

if st.button("Analyze Candidates"):

    results=[]
    cid=1

    for f in uploaded_files:

        text = extract_text(f)

        score,skills = analyze_resume(text,job_description)

        name = extract_name(text)
        email = extract_email(text)
        phone = extract_phone(text)
        exp = extract_experience(text)

        results.append({

            "Candidate ID":f"CAND-{cid}",
            "Candidate Name":name,
            "Resume File":f.name,
            "Score":score,
            "Email":email,
            "Phone":phone,
            "Experience":exp,
            "Matched Skills":", ".join(skills)

        })

        cid += 1

    df = pd.DataFrame(results)

    df = df.sort_values(by="Score",ascending=False)

    st.session_state.results = df
    st.session_state.files = uploaded_files

# ---------------- DISPLAY ----------------

if "results" in st.session_state:

    df = st.session_state.results

    st.subheader("Candidate Dashboard")

    st.dataframe(df,use_container_width=True)

    shortlisted = df[df["Score"] >= threshold]

    st.subheader("Shortlisted Candidates")

    st.dataframe(shortlisted,use_container_width=True)

    report = create_candidate_report(shortlisted)

    with open(report,"rb") as f:

        st.download_button(
            "Download Shortlisted Candidates Info",
            f,
            file_name="shortlisted_candidates.pdf"
        )

    shortlist_files=[]

    for f in st.session_state.files:

        if f.name in shortlisted["Resume File"].values:
            shortlist_files.append(f)

    if shortlist_files:

        pdf_file = merge_resumes(shortlist_files)

        with open(pdf_file,"rb") as f:

            st.download_button(
                "Download All Shortlisted Resumes",
                f,
                file_name="shortlisted_resumes.pdf"
            )

    st.subheader("Candidate Profiles")

    for _,row in df.iterrows():

        with st.expander(f"{row['Candidate Name']} | Score {row['Score']}%"):

            st.write("Email:",row["Email"])
            st.write("Phone:",row["Phone"])
            st.write("Experience:",row["Experience"])
            st.write("Matched Skills:",row["Matched Skills"])
import re


def extract_email(text):

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

    email = re.findall(email_pattern,text)

    return email[0] if email else "Not detected"


def extract_phone(text):

    phone_pattern = r'(\+?\d[\d\-\(\)\s]{8,}\d)'

    phones = re.findall(phone_pattern,text)

    for p in phones:

        digits = re.sub(r'\D','',p)

        if 10 <= len(digits) <= 13:
            return p

    return "Not detected"


def extract_experience(text):

    exp = re.findall(r'\d+\+?\s*(years|yrs)',text)

    return exp[0] if exp else "Not detected"


def extract_name(text):

    lines = text.split("\n")

    for line in lines[:5]:

        if len(line.split()) >= 2 and len(line) < 40:
            return line.title()

    return "Not detected"


def extract_education(text):

    edu = re.findall(r'(bachelor|master|b\.tech|m\.tech|mba|phd)',text.lower())

    return edu[0] if edu else "Not detected"
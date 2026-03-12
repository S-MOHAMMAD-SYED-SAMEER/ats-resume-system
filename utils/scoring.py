from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

STOPWORDS = {
"the","and","with","for","from","this","that","have","will","shall",
"using","used","skills","skill","work","working","experience",
"knowledge","ability","responsible","requirements","including"
}


def clean_words(text):

    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

    words = [w for w in words if w not in STOPWORDS and len(w) > 3]

    return words


def analyze_resume(resume_text, job_description):

    documents = [job_description, resume_text]

    vectorizer = TfidfVectorizer()

    tfidf = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])

    score = int(similarity[0][0] * 100)

    jd_words = set(clean_words(job_description))

    resume_words = set(clean_words(resume_text))

    matched = jd_words.intersection(resume_words)

    matched = list(matched)[:10]

    return score, matched
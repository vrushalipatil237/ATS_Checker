import re
import nltk
# from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords

# Download punkt if not already present
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

# Download stopwords if not already present
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")
    
def clean_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    return set(word for word in tokens if word.isalpha() and word not in stop_words)

def keyword_match_score(resume_text, job_description):
    resume_words = clean_text(resume_text)
    jd_words = clean_text(job_description)
    matched = resume_words.intersection(jd_words)
    total = len(jd_words)
    score = (len(matched) / total * 100) if total > 0 else 0
    return round(score, 2), matched, jd_words - matched

def contact_info_score(resume_text):
    email_present = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text))
    phone_present = bool(re.search(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}', resume_text))
    linkedin_present = 'linkedin.com' in resume_text.lower()
    
    score = (email_present + phone_present + linkedin_present) / 3 * 100
    details = {
        "Email": email_present,
        "Phone": phone_present,
        "LinkedIn": linkedin_present
    }
    return round(score, 2), details

def section_headers_score(resume_text):
    headers = ['education', 'experience', 'skills', 'projects', 'certifications', 'summary', 'objective']
    present = [hdr for hdr in headers if hdr in resume_text.lower()]
    score = len(present) / len(headers) * 100
    missing = set(headers) - set(present)
    return round(score, 2), present, missing

def format_cleanliness_score(resume_text):
    length_ok = len(resume_text) > 200
    weird_chars = re.findall(r'[^\w\s.,@()+-]', resume_text)
    score = 100 if length_ok and not weird_chars else 50 if length_ok else 20
    return score, length_ok, weird_chars

def calculate_ats_score(resume_text, job_description):
    kw_score, matched, missing_kw = keyword_match_score(resume_text, job_description)
    contact_score, contact_details = contact_info_score(resume_text)
    headers_score, present_headers, missing_headers = section_headers_score(resume_text)
    format_score, length_ok, weird_chars = format_cleanliness_score(resume_text)

    overall = round(
        kw_score * 0.5 +
        contact_score * 0.15 +
        headers_score * 0.2 +
        format_score * 0.15,
        2
    )

    details = {
        'keyword': {'score': kw_score, 'matched': matched, 'missing': missing_kw},
        'contact': {'score': contact_score, 'details': contact_details},
        'headers': {'score': headers_score, 'present': present_headers, 'missing': missing_headers},
        'format': {'score': format_score, 'length_ok': length_ok, 'weird_chars': weird_chars}
    }
    return overall, details

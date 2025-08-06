import streamlit as st
import pytesseract
from PIL import Image
import cv2
from pdfminer.high_level import extract_text
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os
import tempfile
import pandas as pd

# Set NLTK data directory inside your app
nltk_data_path = os.path.join(os.path.dirname(__file__), "nltk_data")
nltk.data.path.append(nltk_data_path)
print(nltk.data.find('tokenizers/punkt/english.pickle'))
print("NLTK data paths:", nltk.data.path)
print("Looking for 'punkt':", nltk.data.find('tokenizers/punkt/english.pickle'))


# Extract text from PDF
def extract_text_from_pdf(file_path):
    return extract_text(file_path)

# Extract text from image
def extract_text_from_image(file_path):
    img = cv2.imread(file_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return pytesseract.image_to_string(img)

# Determine file type and extract text
def extract_text_from_file(uploaded_file):
    suffix = uploaded_file.name.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    if suffix.endswith('.pdf'):
        return extract_text_from_pdf(temp_file_path)
    elif suffix.endswith(('.png', '.jpg', '.jpeg')):
        return extract_text_from_image(temp_file_path)
    else:
        return ""

# Clean and tokenize text
def clean_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    return set(word for word in tokens if word.isalpha() and word not in stop_words)

# Calculate ATS score
def calculate_ats_score(resume_text, job_description):
    resume_words = clean_text(resume_text)
    jd_words = clean_text(job_description)

    matched = resume_words.intersection(jd_words)
    total = len(jd_words)
    score = (len(matched) / total * 100) if total > 0 else 0
    return round(score, 2), matched, jd_words - matched

# ---------- Streamlit App ----------
st.set_page_config(page_title="ATS Score Checker", layout="centered")
st.title("📄 ATS Resume Score Checker")

st.markdown("""
Upload your **resume (PDF, PNG, JPG)** and paste a **job description** to check how well your resume matches the job.
""")

uploaded_file = st.file_uploader("📤 Upload Resume", type=['pdf', 'png', 'jpg', 'jpeg'])
job_description = st.text_area("📝 Paste Job Description Here", height=200)

if uploaded_file and job_description:
    with st.spinner("Extracting and analyzing..."):
        resume_text = extract_text_from_file(uploaded_file)
        score, matched, missing = calculate_ats_score(resume_text, job_description)

    st.success(f"✅ ATS Score: **{score}%**")
    st.markdown(f"**✔️ Matched Keywords ({len(matched)}):** {', '.join(sorted(matched))}")
    st.markdown(f"**❌ Missing Keywords ({len(missing)}):** {', '.join(sorted(missing))}")

    # Prepare downloadable report
    max_len = max(len(matched), len(missing))
    matched_list = list(matched) + [''] * (max_len - len(matched))
    missing_list = list(missing) + [''] * (max_len - len(missing))

    report_df = pd.DataFrame({
        "Matched Keywords": matched_list,
        "Missing Keywords": missing_list
    })

    csv_data = report_df.to_csv(index=False)

    st.download_button(
        label="📥 Download ATS Report as CSV",
        data=csv_data,
        file_name="ats_report.csv",
        mime="text/csv"
    )

elif uploaded_file or job_description:
    st.info("Please provide both a resume and job description to proceed.")

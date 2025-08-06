import streamlit as st
import pytesseract
from PIL import Image
import cv2
from pdfminer.high_level import extract_text
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import tempfile
from io import BytesIO
from fpdf import FPDF  # For PDF generation

# Download NLTK data once (remove after first run)
nltk.download('punkt')
nltk.download('stopwords')

# -------- Text extraction --------

def extract_text_from_pdf(file_path):
    return extract_text(file_path)

def extract_text_from_image(file_path):
    img = cv2.imread(file_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return pytesseract.image_to_string(img)

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

# -------- Text cleaning & scoring --------

def clean_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    return set(word for word in tokens if word.isalpha() and word not in stop_words)

def calculate_ats_score(resume_text, job_description):
    resume_words = clean_text(resume_text)
    jd_words = clean_text(job_description)
    matched = resume_words.intersection(jd_words)
    total = len(jd_words)
    score = (len(matched) / total * 100) if total > 0 else 0
    return round(score, 2), matched, jd_words - matched

# -------- PDF report generation --------

def generate_pdf_report(score, matched, missing, job_description, resume_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "ATS Resume Score Report", ln=True, align='C')

    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(0, 10, f"ATS Score: {score}%", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, "Matched Keywords:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, ", ".join(sorted(matched)) if matched else "None")

    pdf.set_font("Arial", size=12)
    pdf.ln(5)
    pdf.cell(0, 10, "Missing Keywords:", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, ", ".join(sorted(missing)) if missing else "None")

    pdf.set_font("Arial", 'B', 12)
    pdf.ln(10)
    pdf.cell(0, 10, "Job Description (excerpt):", ln=True)
    pdf.set_font("Arial", size=10)
    jd_excerpt = (job_description[:500] + '...') if len(job_description) > 500 else job_description
    pdf.multi_cell(0, 8, jd_excerpt)

    pdf.set_font("Arial", 'B', 12)
    pdf.ln(10)
    pdf.cell(0, 10, "Extracted Resume Text (excerpt):", ln=True)
    pdf.set_font("Arial", size=10)
    resume_excerpt = (resume_text[:500] + '...') if len(resume_text) > 500 else resume_text
    pdf.multi_cell(0, 8, resume_excerpt)

    # Generate PDF as a byte string and encode to latin1
    pdf_bytes = pdf.output(dest='S').encode('latin1')

    return pdf_bytes
    
# -------- Streamlit UI --------

st.set_page_config(page_title="ATS Resume Score Checker", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    .appview-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        height: 3em;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        font-size: 1rem;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
    }
    .main {
        padding-left: 25px;
    }
    .title {
        font-weight: bold;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

st.title("📄 ATS Resume Score Checker")

with st.sidebar:
    st.header("Upload & Inputs")
    uploaded_file = st.file_uploader("Upload Resume (PDF, PNG, JPG)", type=['pdf', 'png', 'jpg', 'jpeg'])
    job_description = st.text_area("Paste Job Description", height=200)
    show_raw_resume = st.checkbox("Show Extracted Resume Text")
    show_raw_jd = st.checkbox("Show Job Description Text")

if uploaded_file and job_description.strip():
    with st.spinner("Extracting text and calculating ATS score..."):
        resume_text = extract_text_from_file(uploaded_file)
        score, matched, missing = calculate_ats_score(resume_text, job_description)

    st.subheader(f"✅ ATS Score: {score}%")

    st.markdown(f"**Matched Keywords ({len(matched)}):**")
    st.write(", ".join(sorted(matched)) if matched else "No matched keywords found.")

    st.markdown(f"**Missing Keywords ({len(missing)}):**")
    st.write(", ".join(sorted(missing)) if missing else "No missing keywords.")

    if show_raw_resume:
        st.markdown("### Extracted Resume Text:")
        st.write(resume_text)

    if show_raw_jd:
        st.markdown("### Job Description Text:")
        st.write(job_description)

    # Generate and provide downloadable PDF report
    pdf_report = generate_pdf_report(score, matched, missing, job_description, resume_text)
    st.download_button(
        label="📥 Download ATS Report as PDF",
        data=pdf_report,
        file_name="ats_score_report.pdf",
        mime="application/pdf"
    )
else:
    st.info("Please upload your resume file and paste the job description to check your ATS score.")

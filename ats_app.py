import streamlit as st
import pytesseract
from PIL import Image
import cv2
from pdfminer.high_level import extract_text
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import tempfile

# Download required NLTK data once (can comment out after first run)
nltk.download('punkt')
nltk.download('stopwords')

# --- Functions ---

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

# --- Streamlit UI ---

# Inject custom CSS styles
st.markdown(
    """
    <style>
    .main {
        background-color: #f9fafb;
        color: #0f172a;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: 600;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        cursor: pointer;
    }
    textarea {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 14px;
    }
    .block-container {
        padding: 2rem 3rem;
        max-width: 900px;
        margin: auto;
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 0 15px rgb(0 0 0 / 0.1);
    }
    .title {
        text-align: center;
        color: #2563eb;
        font-weight: 800;
        margin-bottom: 0;
        font-size: 36px;
    }
    .subtitle {
        text-align: center;
        color: #64748b;
        margin-top: 0;
        margin-bottom: 30px;
        font-size: 18px;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="block-container">', unsafe_allow_html=True)

st.markdown('<h1 class="title">📄 ATS Resume Score Checker</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload your resume document and paste the job description below.</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 Upload Resume (PDF, PNG, JPG)", type=['pdf', 'png', 'jpg', 'jpeg'])

job_description = st.text_area("📝 Paste Job Description Here", height=180)

if st.button("Calculate ATS Score"):
    if uploaded_file and job_description.strip():
        with st.spinner("Extracting text and calculating score..."):
            resume_text = extract_text_from_file(uploaded_file)
            score, matched, missing = calculate_ats_score(resume_text, job_description)
        st.success(f"✅ ATS Score: **{score}%**")
        st.markdown(f"**✔️ Matched Keywords ({len(matched)}):** {', '.join(sorted(matched))}")
        st.markdown(f"**❌ Missing Keywords ({len(missing)}):** {', '.join(sorted(missing))}")
    else:
        st.warning("⚠️ Please upload a resume file and enter a job description.")

st.markdown('</div>', unsafe_allow_html=True)

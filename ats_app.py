import streamlit as st
from extraction import extract_text_from_file
from scoring import calculate_ats_score
from pdf_report import generate_pdf_report

# ========== NLTK Setup (FIX for punkt_tab error) ==========
import nltk
import os
import shutil

# Manually clear corrupted punkt folder
try:
    punkt_path = os.path.join(nltk.data.find('tokenizers'), 'punkt')
    if os.path.exists(punkt_path):
        shutil.rmtree(punkt_path)
except:
    pass  # Safe to ignore

# Set custom nltk_data path
nltk_path = os.path.join(os.path.dirname(__file__), "nltk_data")
nltk.data.path.append(nltk_path)

# Re-download clean data
#nltk.download('punkt')
#nltk.download('stopwords')

# ===== Streamlit UI Config =====
st.set_page_config(page_title="ATS Resume Score Checker", layout="wide")

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

# ===== Sidebar Inputs =====
with st.sidebar:
    st.header("Upload & Inputs")
    uploaded_file = st.file_uploader("Upload Resume (PDF or Image)", type=['pdf', 'png', 'jpg', 'jpeg'])
    job_description = st.text_area("Paste Job Description", height=200)
    show_raw_resume = st.checkbox("Show Extracted Resume Text")
    show_raw_jd = st.checkbox("Show Job Description Text")

# ===== Main Logic =====
if uploaded_file and job_description.strip():
    with st.spinner("Extracting text and calculating ATS score..."):
        resume_text = extract_text_from_file(uploaded_file)
        overall_score, details = calculate_ats_score(resume_text, job_description)

    st.subheader(f"✅ Overall ATS Score: {overall_score}%")

    st.markdown("### Sectional Scores:")
    st.write(f"- **Keyword Match Score:** {details['keyword']['score']}%")
    st.write(f"- **Contact Info Score:** {details['contact']['score']}%")
    st.write(f"- **Section Headers Score:** {details['headers']['score']}%")
    st.write(f"- **Format Cleanliness Score:** {details['format']['score']}%")

    if show_raw_resume:
        st.markdown("### Extracted Resume Text:")
        st.write(resume_text)

    if show_raw_jd:
        st.markdown("### Job Description Text:")
        st.write(job_description)

    # ===== Downloadable PDF =====
    pdf_report = generate_pdf_report(overall_score, details, job_description, resume_text)
    st.download_button(
        label="📥 Download ATS Report as PDF",
        data=pdf_report,
        file_name="ats_score_report.pdf",
        mime="application/pdf"
    )
else:
    st.info("Please upload your resume file and paste the job description to check your ATS score.")

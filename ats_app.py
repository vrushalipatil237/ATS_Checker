import streamlit as st
import pytesseract
from PIL import Image
import cv2
from pdfminer.high_level import extract_text
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import tempfile
import re

# Download NLTK data if not present
nltk.download('punkt')
nltk.download('stopwords')

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
    return [word for word in tokens if word.isalpha() and word not in stop_words]

def keyword_match_score(resume_text, job_description):
    jd_keywords = set(clean_text(job_description))
    resume_words = set(clean_text(resume_text))
    matched = resume_words.intersection(jd_keywords)
    score = len(matched) / len(jd_keywords) if jd_keywords else 0
    return round(score * 100, 2), matched, jd_keywords - matched

def job_title_score(resume_title, job_title):
    resume_title = resume_title.lower()
    job_title = job_title.lower()
    if job_title in resume_title or resume_title in job_title:
        return 100
    return 0

def skills_score(resume_skills, job_skills):
    resume_skills_set = set([s.lower().strip() for s in resume_skills])
    job_skills_set = set([s.lower().strip() for s in job_skills])
    matched = resume_skills_set.intersection(job_skills_set)
    score = len(matched) / len(job_skills_set) if job_skills_set else 0
    return round(score * 100, 2), matched, job_skills_set - matched

def certifications_score(resume_certs, job_certs):
    resume_certs_set = set([c.lower().strip() for c in resume_certs])
    job_certs_set = set([c.lower().strip() for c in job_certs])
    matched = resume_certs_set.intersection(job_certs_set)
    score = len(matched) / len(job_certs_set) if job_certs_set else 0
    return round(score * 100, 2), matched, job_certs_set - matched

def quantify_achievements_score(resume_text):
    numbers = re.findall(r'\d+', resume_text)
    if numbers:
        return 100
    return 0

def generate_report(scores):
    report = f"""
### ATS Score Report

**Keyword Match:** {scores['keyword_score']}%  
Matched Keywords: {', '.join(sorted(scores['keyword_matched']))}  
Missing Keywords: {', '.join(sorted(scores['keyword_missing']))}  

**Job Title Match:** {scores['title_score']}%  

**Skills Match:** {scores['skills_score']}%  
Matched Skills: {', '.join(sorted(scores['skills_matched']))}  
Missing Skills: {', '.join(sorted(scores['skills_missing']))}  

**Certifications Match:** {scores['certs_score']}%  
Matched Certifications: {', '.join(sorted(scores['certs_matched']))}  
Missing Certifications: {', '.join(sorted(scores['certs_missing']))}  

**Quantified Achievements:** {scores['achievements_score']}%  

**Final ATS Score:** {scores['final_score']}%
"""
    return report

# --- Streamlit UI ---

st.set_page_config(page_title="ATS Resume Score Checker", layout="centered")
st.title("📄 ATS Resume Score Checker")

st.markdown("""
Upload your **resume (PDF, PNG, JPG)** and enter the **job description details** below to check how well your resume matches the job.
""")

uploaded_file = st.file_uploader("📤 Upload Resume", type=['pdf', 'png', 'jpg', 'jpeg'])

st.header("Job Description Details")
job_title = st.text_input("Job Title (e.g. Software Engineer)")
job_description = st.text_area("Full Job Description Text")
job_skills_input = st.text_input("Required Skills (comma separated, e.g. Python, SQL, AWS)")
job_certs_input = st.text_input("Required Certifications (comma separated, e.g. AWS Solutions Architect, PMP)")

if uploaded_file and job_title and job_description:
    with st.spinner("Extracting and analyzing..."):
        resume_text = extract_text_from_file(uploaded_file)
        
        # Extract job skills and certs lists
        job_skills = [s.strip() for s in job_skills_input.split(",")] if job_skills_input else []
        job_certs = [c.strip() for c in job_certs_input.split(",")] if job_certs_input else []
        
        # For simplicity, let's try to extract resume title from first line of resume text
        resume_lines = resume_text.strip().split("\n")
        resume_title = resume_lines[0] if resume_lines else ""
        
        # Here you could also parse skills and certs from resume_text if you want
        # For demo, let's assume user enters them manually or use basic extraction from resume text (optional)
        # For now, let's extract skills from resume text keywords intersection
        resume_words = clean_text(resume_text)
        resume_skills = list(set(resume_words).intersection(set([s.lower() for s in job_skills])))
        resume_certs = list(set(resume_words).intersection(set([c.lower() for c in job_certs])))
        
        keyword_score, keyword_matched, keyword_missing = keyword_match_score(resume_text, job_description)
        title_score = job_title_score(resume_title, job_title)
        skills_score_val, skills_matched, skills_missing = skills_score(resume_skills, job_skills)
        certs_score, certs_matched, certs_missing = certifications_score(resume_certs, job_certs)
        achievements_score = quantify_achievements_score(resume_text)
        
        # Weighted final score - adjust weights as you prefer
        final_score = round(
            keyword_score * 0.4 +
            title_score * 0.2 +
            skills_score_val * 0.2 +
            certs_score * 0.1 +
            achievements_score * 0.1, 2
        )
        
        scores = {
            "keyword_score": keyword_score,
            "keyword_matched": keyword_matched,
            "keyword_missing": keyword_missing,
            "title_score": title_score,
            "skills_score": skills_score_val,
            "skills_matched": skills_matched,
            "skills_missing": skills_missing,
            "certs_score": certs_score,
            "certs_matched": certs_matched,
            "certs_missing": certs_missing,
            "achievements_score": achievements_score,
            "final_score": final_score
        }
    
    st.success(f"✅ Final ATS Score: **{final_score}%**")
    
    st.markdown(f"### Details")
    st.markdown(f"**Keyword Match:** {keyword_score}%")
    st.markdown(f"- Matched: {', '.join(sorted(keyword_matched)) if keyword_matched else 'None'}")
    st.markdown(f"- Missing: {', '.join(sorted(keyword_missing)) if keyword_missing else 'None'}")
    
    st.markdown(f"**Job Title Match:** {title_score}%")
    
    st.markdown(f"**Skills Match:** {skills_score_val}%")
    st.markdown(f"- Matched: {', '.join(sorted(skills_matched)) if skills_matched else 'None'}")
    st.markdown(f"- Missing: {', '.join(sorted(skills_missing)) if skills_missing else 'None'}")
    
    st.markdown(f"**Certifications Match:** {certs_score}%")
    st.markdown(f"- Matched: {', '.join(sorted(certs_matched)) if certs_matched else 'None'}")
    st.markdown(f"- Missing: {', '.join(sorted(certs_missing)) if certs_missing else 'None'}")
    
    st.markdown(f"**Quantified Achievements:** {achievements_score}%")
    
    # Downloadable report
    report_text = generate_report(scores)
    st.download_button(
        label="📥 Download ATS Report",
        data=report_text,
        file_name="ats_score_report.md",
        mime="text/markdown"
    )
    
elif uploaded_file or job_title or job_description:
    st.info("Please upload a resume and fill in Job Title and Job Description to calculate ATS score.")
else:
    st.info("Upload your resume and enter job description details to start.")

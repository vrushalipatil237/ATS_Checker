import pytesseract
from PIL import Image
import cv2
import os
from pdfminer.high_level import extract_text
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

# Make sure NLTK resources are downloaded
nltk.download('punkt')
nltk.download('stopwords')

# Set tesseract path if needed
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_pdf(file_path):
    return extract_text(file_path)

def extract_text_from_image(file_path):
    img = cv2.imread(file_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img)
    return text

def extract_text_from_file(file_path):
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        return extract_text_from_image(file_path)
    else:
        raise ValueError("Unsupported file format")

def clean_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    words = [word for word in tokens if word.isalpha() and word not in stop_words]
    return set(words)

def calculate_ats_score(resume_text, job_description):
    resume_words = clean_text(resume_text)
    jd_words = clean_text(job_description)

    matched_keywords = resume_words.intersection(jd_words)
    total_keywords = len(jd_words)

    if total_keywords == 0:
        return 0

    score = len(matched_keywords) / total_keywords * 100
    return round(score, 2), matched_keywords, jd_words - matched_keywords

# -------- Main Function to Use -------- #
def ats_score_checker(file_path, job_description):
    try:
        resume_text = extract_text_from_file(file_path)
        score, matched, missing = calculate_ats_score(resume_text, job_description)
        print(f"✅ ATS Score: {score}%")
        print(f"✔️ Matched Keywords: {matched}")
        print(f"❌ Missing Keywords: {missing}")
    except Exception as e:
        print(f"Error: {e}")

# -------- Example Usage -------- #
if __name__ == "__main__":
    resume_file = "sample_resume.pdf"  # or .png / .jpg
    job_description = """
    Looking for a Python developer with experience in Django, REST APIs, SQL, and cloud platforms such as AWS or Azure.
    Must have strong knowledge of data structures and problem-solving.
    """

    ats_score_checker(resume_file, job_description)

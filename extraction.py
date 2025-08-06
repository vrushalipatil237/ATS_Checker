import pytesseract
import cv2
from pdfminer.high_level import extract_text
import tempfile
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

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

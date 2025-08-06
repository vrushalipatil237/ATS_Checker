from pdfminer.high_level import extract_text
import tempfile
import requests

def extract_text_from_pdf(file_path):
    return extract_text(file_path)

def extract_text_from_image(file_path):
    api_key = 'helloworld'  # Replace with your actual key if needed
    with open(file_path, 'rb') as image_file:
        response = requests.post(
            'https://api.ocr.space/parse/image',
            files={'filename': image_file},
            data={'apikey': api_key, 'language': 'eng'}
        )

    result = response.json()
    if result.get("IsErroredOnProcessing"):
        return "Error: " + result.get("ErrorMessage", ["Unknown error"])[0]
    else:
        return result["ParsedResults"][0]["ParsedText"]

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

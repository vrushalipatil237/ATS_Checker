from fpdf import FPDF

def generate_pdf_report(overall_score, details, job_description, resume_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "ATS Resume Score Report", ln=True, align='C')

    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Overall ATS Score: {overall_score}%", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Keyword Match", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Score: {details['keyword']['score']}%", ln=True)
    pdf.cell(0, 10, f"Matched Keywords: {', '.join(sorted(details['keyword']['matched'])) or 'None'}", ln=True)
    pdf.cell(0, 10, f"Missing Keywords: {', '.join(sorted(details['keyword']['missing'])) or 'None'}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Contact Info Presence", ln=True)
    pdf.set_font("Arial", size=12)
    for k, v in details['contact']['details'].items():
        pdf.cell(0, 10, f"{k}: {'Yes' if v else 'No'}", ln=True)
    pdf.cell(0, 10, f"Score: {details['contact']['score']}%", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Section Headers", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Score: {details['headers']['score']}%", ln=True)
    pdf.cell(0, 10, f"Present: {', '.join(details['headers']['present']) or 'None'}", ln=True)
    pdf.cell(0, 10, f"Missing: {', '.join(details['headers']['missing']) or 'None'}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Format Cleanliness", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Score: {details['format']['score']}%", ln=True)
    pdf.cell(0, 10, f"Length OK: {'Yes' if details['format']['length_ok'] else 'No'}", ln=True)
    weird_chars = ', '.join(set(details['format']['weird_chars'])) or 'None'
    pdf.cell(0, 10, f"Weird Characters Found: {weird_chars}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
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

    return pdf.output(dest='S').encode('latin1')

'''module that extracts text from pdf and job description text'''
import pdfplumber 


def extract_pdf_text(pdf_path):
    text=""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error occurred while extracting text from PDF: {e}")
        return ""


if __name__ == "__main__":
    pdf_path = r"E:\internship\resume_matcher\utils\sample.pdf"
    extracted_text = extract_pdf_text(pdf_path)
    print(extracted_text)
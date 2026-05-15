from utils.extract import extract_pdf_text
from utils.clean import clean_text
from utils.resume_matcher import analyze_resume

def main(pdf_path, job_description):
    extracted_resume = extract_pdf_text(pdf_path)
    result = analyze_resume(extracted_resume, job_description)
    print(result)
    return result
    


if __name__ == "__main__":
    pdf_path = r"E:\internship\resume_matcher\sample.pdf"
    job_description = """"""
    main(pdf_path, job_description)
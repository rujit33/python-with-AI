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
    job_description = """We are looking for a skilled software engineer with experience in Python, machine learning, and data analysis. The ideal candidate should have a strong background in algorithms, data structures, and software design principles. Experience with cloud platforms like AWS or Azure is a plus. The candidate should also be proficient in version control systems like Git and have excellent problem-solving skills."""
    main(pdf_path, job_description)
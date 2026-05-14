# Resume Matcher

- TF-IDF cosine similarity
- NLP keyword extraction with spaCy
- Skill taxonomy grouping
- Match/missing skill detection
- Interactive Gradio web interface

The system extracts text from a PDF resume, analyzes the job description, detects relevant technical skills, groups them into categories, and generates a match score with a visual skill breakdown.

---


# Technologies Used

| Technology | Purpose |
|---|---|
| spaCy | NLP processing |
| scikit-learn | TF-IDF + cosine similarity |
| pdfplumber | PDF text extraction |
| NumPy | Vector operations |
| Gradio | Web interface |

---

# Project Structure

```text
resume_matcher/
│
├── utils/
│   ├── extract.py
│   ├── resume_matcher.py
│   └── taxonomy.py
│
├── app.py
├── main.py
├── install.py
└── README.md

```

# How the System Works

## 1. PDF Text Extraction

### `extract.py`

- Reads uploaded résumé PDFs
- Extracts text page-by-page
- Returns plain text

Uses:

```python
pdfplumber
```

---

## 2. NLP Keyword Extraction

### `resume_matcher.py`

spaCy extracts:

- nouns
- noun phrases
- technical terms
- important keywords

Example keywords:

```text
python
machine learning
aws
docker
data analysis
```

---

## 3. Skill Taxonomy Classification

### `taxonomy.py`

Keywords are grouped into categories like:

- Web Development
- Data Science & ML
- Cloud & DevOps
- Databases
- Security

Example:

```python
"python"      → Programming Languages
"docker"      → Cloud & DevOps
"tensorflow"  → Data Science & ML
```

---

## 4. Match Score Calculation

Uses:

```python
TfidfVectorizer
cosine_similarity
```

to compare:

- resume text
- job description

Final output:

```text
0 – 100%
```

---

## 5. Skill Gap Analysis

Checks:

- matched skills
- missing skills

Example:

```text
Matched:
- python
- tensorflow
- git

Missing:
- kubernetes
- aws
```

---

# Set up

```powershell
cd "resume_matcher"
```

# Install spaCy Model

```bash
python -m spacy download en_core_web_md
```

Required for vector similarity.

---

## Run Setup File

Before running the app:

```bash
python install.py
```

Downloads required NLTK resources.

---

# Running the Application

Start the Gradio app:

```bash
python app.py
```

Gradio will generate a local URL:

```text
http://127.0.0.1:7860
```

Open it in your browser.

---

# Usage

## Step 1

Upload resume PDF.

---

## Step 2

Paste job description.

Example:

```text
We are looking for a Python developer with experience in
machine learning, AWS, Docker, and REST APIs.
```

---

## Step 3

Click:

```text
Analyse →
```

---

## Step 4

View:

- Match percentage
- Matched skills
- Missing skills
- Category breakdown

---

# Example Output

## Match Score

```text
78%
```

---

## Skill Breakdown

### Data Science & ML

```text
Matched:
- machine learning
- pandas
- numpy

Missing:
- tensorflow
```

---

### Cloud & DevOps

```text
Matched:
- docker

Missing:
- kubernetes
- aws
```

---

# File Explanations

## `extract.py`

Handles:

- PDF reading
- text extraction
- extraction errors

Main function:

```python
extract_pdf_text(pdf_path)
```

---

## `resume_matcher.py`

Core NLP engine.

Contains:

- keyword extraction
- similarity scoring
- taxonomy matching
- skill analysis

Main functions:

```python
extract_keywords()
get_similarity()
analyze_resume()
```

---

## `taxonomy.py`

Stores categorized technical skills.

Example:

```python
TAXONOMY = {
    "Web Development": [...],
    "Cloud & DevOps": [...],
}
```

---

## `main.py`

Main backend pipeline.

Flow:

```text
PDF → Extract Text → Analyze → Return Result
```

---

## `app.py`

Gradio frontend.

Handles:

- UI rendering
- file uploads
- result display
- skill cards
- progress bars

---

## `install.py`

Downloads NLTK datasets.

Run once before starting the app.

---

# Example Workflow

```text
Upload Resume
      ↓
Extract PDF Text
      ↓
Extract Keywords
      ↓
Categorize Skills
      ↓
Compute Similarity
      ↓
Display Results
```

---

# Current Limitations

- Exact keyword matching may miss synonyms
- No OCR support
- No DOCX support
- TF-IDF is not deep semantic understanding
- Scanned PDFs may fail

---

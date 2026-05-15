
"""Resume matcher — taxonomy-based skill grouping + TF-IDF match score."""
import spacy
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
nlp = spacy.load("en_core_web_md")
from .taxonomy import TAXONOMY


TAXONOMY= TAXONOMY()


# Build a flat lookup: seed_word → category
_SEED_LOOKUP: dict[str, str] = {}
for _cat, _seeds in TAXONOMY.items():
    for _s in _seeds:
        _SEED_LOOKUP[_s] = _cat


#  Helpers 

def _phrase_vector(phrase: str) -> np.ndarray:
    doc = nlp(phrase.lower())
    vecs = [t.vector for t in doc if t.has_vector]
    return np.mean(vecs, axis=0) if vecs else np.zeros(nlp.vocab.vectors_length)

def _best_category(keyword: str) -> str:
    """Return the taxonomy category best matching a keyword."""
    kw = keyword.lower()

    # 1. Exact / substring match against seeds
    for seed, cat in _SEED_LOOKUP.items():
        if seed in kw or kw in seed:
            return cat

    # 2. Vector similarity against category centroids
    kw_vec = _phrase_vector(kw)
    if np.linalg.norm(kw_vec) == 0:
        return "Other"

    best_cat, best_sim = "Other", 0.4   # similarity floor
    for cat, seeds in TAXONOMY.items():
        cat_vec = np.mean([_phrase_vector(s) for s in seeds[:6]], axis=0)
        sim = cosine_similarity([kw_vec], [cat_vec])[0][0]
        if sim > best_sim:
            best_sim, best_cat = sim, cat

    return best_cat


#  Core functions 

def extract_keywords(text: str) -> set[str]:
    """Extract meaningful skill terms using spaCy POS filtering."""
    doc = nlp(text.lower())
    keywords: set[str] = set()

    for token in doc:
        if (token.pos_ in ("NOUN", "PROPN")
                and not token.is_stop
                and not token.is_punct
                and len(token.text) > 2):
            keywords.add(token.lemma_)

    for chunk in doc.noun_chunks:
        tokens = [t.lemma_ for t in chunk
                  if not t.is_stop and not t.is_punct and len(t.text) > 2]
        phrase = " ".join(tokens)
        if 1 < len(tokens) <= 2 and len(phrase) > 3:
            keywords.add(phrase)

    return keywords


def get_similarity(resume: str, jd: str) -> float:
    """TF-IDF cosine similarity (0–100)."""
    vec = TfidfVectorizer(stop_words="english")
    tfidf = vec.fit_transform([jd, resume])
    return round(float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]) * 100, 1)


def analyze_resume(resume_text: str, jd_text: str) -> dict:
    """
    Returns:
        match_score  : float
        categories   : { category_name: { matched: [...], missing: [...] } }
    """
    jd_keywords  = extract_keywords(jd_text)
    score        = get_similarity(resume_text, jd_text)
    resume_lower = resume_text.lower()

    # Sort each keyword into matched / missing
    categories: dict[str, dict] = {}
    for kw in sorted(jd_keywords):
        cat = _best_category(kw)
        bucket = categories.setdefault(cat, {"matched": [], "missing": []})
        if kw in resume_lower:
            bucket["matched"].append(kw)
        else:
            bucket["missing"].append(kw)

    # Drop empty categories
    categories = {
        cat: data for cat, data in categories.items()
        if data["matched"] or data["missing"]
    }

    return {
        "match_score": score,
        "categories":  categories,
    }
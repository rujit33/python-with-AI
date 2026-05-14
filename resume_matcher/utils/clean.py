import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


stop_words = set(stopwords.words("english"))

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9 ]", " ", text)

    tokens = word_tokenize(text)

    filtered = [w for w in tokens if w not in stop_words]

    return " ".join(filtered)


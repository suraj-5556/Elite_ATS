"""
NLP Scorer: Computes semantic similarity between resume and job description
using TF-IDF vectorization + cosine similarity.
Weight in final score: 35%

Also extracts matched/missing skills using keyword overlap.
"""

import re
import logging
from typing import Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# Comprehensive tech skill keyword list
TECH_SKILLS = {
    # Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
    'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab',
    # Web
    'react', 'vue', 'angular', 'node.js', 'express', 'django', 'flask',
    'fastapi', 'spring', 'html5', 'css3', 'sass', 'graphql', 'rest',
    # Data/ML
    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
    'spark', 'hadoop', 'kafka', 'airflow', 'mlflow', 'nlp', 'bert',
    'transformers', 'opencv', 'xgboost', 'lightgbm',
    # Databases
    'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
    'cassandra', 'dynamodb', 'sqlite',
    # Cloud/DevOps
    'aws', 'gcp', 'azure', 'docker', 'kubernetes', 'terraform', 'ansible',
    'jenkins', 'github actions', 'ci/cd', 'linux', 'bash', 'git',
    # Soft skills
    'leadership', 'communication', 'teamwork', 'problem-solving', 'agile',
    'scrum', 'project management',
}


def _preprocess(text: str) -> str:
    """Lowercase, remove punctuation, normalize spaces."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s.#+]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def compute_nlp_score(resume_text: str, jd_text: str) -> float:
    """
    Returns a score 0–100 using TF-IDF cosine similarity.
    TF-IDF captures term importance relative to corpus, making it
    more robust than simple word overlap.
    """
    if not resume_text or not jd_text:
        return 0.0

    try:
        docs = [_preprocess(resume_text), _preprocess(jd_text)]
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),   # Unigrams + bigrams for better context
            stop_words='english',
            max_features=10_000,
        )
        tfidf_matrix = vectorizer.fit_transform(docs)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(similarity) * 100, 2)
    except Exception as e:
        logger.error(f"NLP scoring error: {e}")
        return 0.0


def extract_skills(resume_text: str, jd_text: str) -> Tuple[list, list]:
    """
    Compare skill keywords between resume and JD.
    Returns (matched_skills, missing_skills).
    """
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()

    # Find skills mentioned in JD
    jd_skills = {skill for skill in TECH_SKILLS if skill in jd_lower}

    # Find skills in resume
    resume_skills = {skill for skill in jd_skills if skill in resume_lower}

    matched = sorted(list(resume_skills))
    missing = sorted(list(jd_skills - resume_skills))

    return matched, missing

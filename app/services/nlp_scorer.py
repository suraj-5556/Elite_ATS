import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

def calculate_skill_overlap(resume_skills: List[str], jd_required: List[str], jd_preferred: List[str]) -> Dict:
    resume_skills_lower = {s.lower() for s in resume_skills}
    required_lower = {s.lower() for s in jd_required}
    preferred_lower = {s.lower() for s in jd_preferred}
    
    matched_required = resume_skills_lower.intersection(required_lower)
    matched_preferred = resume_skills_lower.intersection(preferred_lower)
    missing_required = required_lower - resume_skills_lower
    missing_preferred = preferred_lower - resume_skills_lower
    
    req_score = len(matched_required) / max(len(required_lower), 1)
    pref_score = len(matched_preferred) / max(len(preferred_lower), 1)
    
    # Weighted: required skills matter more
    skill_score = (req_score * 0.75 + pref_score * 0.25)
    
    return {
        'matched_required': [s.title() for s in matched_required],
        'matched_preferred': [s.title() for s in matched_preferred],
        'missing_required': [s.title() for s in missing_required],
        'missing_preferred': [s.title() for s in missing_preferred],
        'required_score': round(req_score, 3),
        'preferred_score': round(pref_score, 3),
        'skill_overlap_score': round(skill_score, 3),
    }

def calculate_tfidf_similarity(resume_text: str, jd_text: str) -> float:
    try:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return round(float(similarity), 3)
    except Exception as e:
        logger.error(f"TF-IDF error: {e}")
        return 0.0

def calculate_keyword_density(resume_text: str, jd_keywords: List[str]) -> float:
    if not jd_keywords:
        return 0.0
    resume_lower = resume_text.lower()
    matched = sum(1 for kw in jd_keywords if kw.lower() in resume_lower)
    return round(matched / len(jd_keywords), 3)

def calculate_experience_match(resume_years: float, required_years: float) -> float:
    if required_years == 0:
        return 1.0
    if resume_years >= required_years:
        return 1.0
    elif resume_years >= required_years * 0.7:
        return 0.7
    elif resume_years >= required_years * 0.5:
        return 0.5
    else:
        return max(0.2, resume_years / required_years)

def calculate_ats_score(resume_text: str, jd_text: str, skill_overlap: Dict) -> int:
    """ATS-style keyword matching score"""
    resume_lower = resume_text.lower()
    jd_words = set(jd_text.lower().split())
    
    # Filter meaningful words
    meaningful = {w for w in jd_words if len(w) > 3}
    matched = sum(1 for w in meaningful if w in resume_lower)
    
    base_score = int((matched / max(len(meaningful), 1)) * 60)
    skill_bonus = int(skill_overlap['required_score'] * 30)
    format_bonus = 10 if len(resume_text) > 500 else 5
    
    return min(100, base_score + skill_bonus + format_bonus)

def compute_nlp_scores(resume_data: Dict, jd_data: Dict) -> Dict:
    logger.info("Computing NLP similarity scores")
    
    resume_text = resume_data.get('raw_text', '')
    jd_text = jd_data.get('raw_text', '')
    
    skill_overlap = calculate_skill_overlap(
        resume_data.get('skills', []),
        jd_data.get('required_skills', []),
        jd_data.get('preferred_skills', [])
    )
    
    tfidf_score = calculate_tfidf_similarity(resume_text, jd_text)
    keyword_density = calculate_keyword_density(resume_text, jd_data.get('keywords', []))
    experience_match = calculate_experience_match(
        resume_data.get('experience_years', 0),
        jd_data.get('experience_required', 0)
    )
    ats_score = calculate_ats_score(resume_text, jd_text, skill_overlap)
    
    # Composite NLP score
    nlp_score = (
        skill_overlap['skill_overlap_score'] * 0.40 +
        tfidf_score * 0.25 +
        keyword_density * 0.20 +
        experience_match * 0.15
    )
    
    return {
        'skill_overlap': skill_overlap,
        'tfidf_similarity': tfidf_score,
        'keyword_density': keyword_density,
        'experience_match': round(experience_match, 3),
        'ats_score': ats_score,
        'nlp_composite_score': round(nlp_score, 3),
    }

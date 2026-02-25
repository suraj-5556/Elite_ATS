"""
ML Scorer: Uses a Gradient Boosting classifier trained on resume features.
Weight in final score: 30%

Feature engineering:
- Resume length (word count)
- Keyword density
- Section presence (education, experience, skills, etc.)
- Quantified achievements (numbers/metrics in resume)
- Action verb count
"""

import re
import os
import logging
import numpy as np
from typing import Tuple

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'ml_models', 'inference', 'gb_model.pkl'
)

# Lazy-load model to avoid startup overhead
_model = None
_vectorizer = None

ACTION_VERBS = {
    'led', 'built', 'designed', 'developed', 'implemented', 'managed',
    'created', 'launched', 'improved', 'increased', 'reduced', 'optimized',
    'delivered', 'architected', 'deployed', 'automated', 'scaled', 'mentored',
    'collaborated', 'achieved', 'drove', 'engineered', 'spearheaded',
}

SECTION_KEYWORDS = {
    'education': ['education', 'degree', 'university', 'college', 'bachelor', 'master', 'phd', 'gpa'],
    'experience': ['experience', 'work history', 'employment', 'internship', 'position'],
    'skills': ['skills', 'technologies', 'tech stack', 'proficiency', 'expertise'],
    'projects': ['projects', 'portfolio', 'github', 'open source'],
    'certifications': ['certification', 'certified', 'license', 'aws certified', 'google certified'],
}


def _extract_features(resume_text: str, jd_text: str) -> np.ndarray:
    """
    Extract numerical feature vector from resume + JD pair.
    These features are what the Gradient Boosting model operates on.
    """
    r = resume_text.lower()
    j = jd_text.lower()

    words = r.split()
    word_count = len(words)

    # Feature 1: Word count (normalized)
    f_word_count = min(word_count / 800, 2.0)

    # Feature 2: Keyword overlap ratio
    jd_words = set(j.split())
    resume_words = set(words)
    overlap = len(jd_words & resume_words) / max(len(jd_words), 1)
    f_keyword_overlap = overlap

    # Feature 3: Section coverage score
    section_score = sum(
        1 for kws in SECTION_KEYWORDS.values()
        if any(kw in r for kw in kws)
    ) / len(SECTION_KEYWORDS)
    f_sections = section_score

    # Feature 4: Quantified achievements (numbers like "increased by 40%", "managed 10 engineers")
    numbers = re.findall(r'\b\d+[\%\+]?\b', resume_text)
    f_metrics = min(len(numbers) / 10, 1.0)

    # Feature 5: Action verb usage
    action_count = sum(1 for w in words if w in ACTION_VERBS)
    f_action_verbs = min(action_count / 15, 1.0)

    # Feature 6: Resume length penalty/bonus (too short = bad, very long = minor penalty)
    if word_count < 200:
        f_length_quality = 0.3
    elif word_count < 400:
        f_length_quality = 0.6
    elif word_count <= 1000:
        f_length_quality = 1.0
    else:
        f_length_quality = 0.85

    # Feature 7: Technical term density
    tech_terms = re.findall(
        r'\b(python|java|aws|sql|docker|react|ml|api|cloud|data|ai|backend|frontend)\b', r
    )
    f_tech_density = min(len(tech_terms) / 20, 1.0)

    return np.array([[
        f_word_count, f_keyword_overlap, f_sections,
        f_metrics, f_action_verbs, f_length_quality, f_tech_density
    ]])


def _load_model():
    """Load saved model if available; fall back to rule-based scorer."""
    global _model
    if _model is not None:
        return _model

    try:
        import pickle
        model_file = os.path.abspath(MODEL_PATH)
        if os.path.exists(model_file):
            with open(model_file, 'rb') as f:
                _model = pickle.load(f)
            logger.info("Gradient Boosting model loaded from disk.")
        else:
            logger.warning("No trained model found. Using rule-based ML fallback.")
            _model = None
    except Exception as e:
        logger.error(f"Model load error: {e}")
        _model = None

    return _model


def compute_ml_score(resume_text: str, jd_text: str) -> Tuple[float, str]:
    """
    Returns (score_0_to_100, model_version).
    Uses trained GB model if available, otherwise rule-based fallback.
    """
    features = _extract_features(resume_text, jd_text)
    model = _load_model()

    if model is not None:
        try:
            # predict_proba returns [prob_class_0, prob_class_1]
            prob = model.predict_proba(features)[0][1]
            score = round(float(prob) * 100, 2)
            return score, "gb_v1.0"
        except Exception as e:
            logger.error(f"Model inference error: {e}, falling back to rule-based")

    # ── Rule-based fallback ───────────────────────────────────────────────────
    f = features[0]
    # Weighted combination of our hand-engineered features
    weights = [0.15, 0.25, 0.20, 0.15, 0.10, 0.10, 0.05]
    score = sum(w * v for w, v in zip(weights, f)) * 100
    score = round(min(max(score, 0), 100), 2)
    return score, "rule_based_v1.0"


def compute_ats_score(resume_text: str, jd_text: str) -> float:
    """
    Simulate ATS (Applicant Tracking System) score.
    Focuses on keyword matching, formatting signals, and section presence.
    """
    r = resume_text.lower()
    j = jd_text.lower()

    # Keyword match score
    jd_terms = set(re.findall(r'\b[a-z][a-z0-9+#.]{2,}\b', j)) - {
        'the', 'and', 'for', 'are', 'you', 'will', 'with', 'have', 'this',
        'that', 'from', 'they', 'been', 'has', 'not', 'but', 'all', 'were'
    }
    if not jd_terms:
        return 50.0

    matched = sum(1 for t in jd_terms if t in r)
    kw_score = matched / len(jd_terms)

    # Section presence
    sections_present = sum(
        1 for kws in SECTION_KEYWORDS.values()
        if any(kw in r for kw in kws)
    )
    section_score = sections_present / len(SECTION_KEYWORDS)

    ats = (kw_score * 0.70 + section_score * 0.30) * 100
    return round(min(max(ats, 0), 100), 2)

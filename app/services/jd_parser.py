import re
import logging
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from app.services.resume_parser import SKILLS_DB

logger = logging.getLogger(__name__)

try:
    stop_words = set(stopwords.words('english'))
except:
    nltk.download('stopwords', quiet=True)
    stop_words = set(stopwords.words('english'))

EXPERIENCE_PATTERNS = [
    r'(\d+)\+?\s*years?\s+of\s+(?:relevant\s+)?experience',
    r'(\d+)\+?\s*years?\s+experience',
    r'minimum\s+(\d+)\+?\s*years?',
    r'(\d+)\+?\s*yrs?\.?\s+(?:of\s+)?experience',
    r'at\s+least\s+(\d+)\s+years?',
]

SENIORITY_KEYWORDS = {
    'entry': ['entry level', 'junior', 'fresher', 'graduate', '0-2 years', '0-1 year', 'intern'],
    'mid': ['mid level', 'intermediate', '2-5 years', '3-5 years', '2+ years', '3+ years'],
    'senior': ['senior', 'lead', '5+ years', '7+ years', '5-10 years', 'principal', 'staff engineer'],
    'manager': ['manager', 'director', 'head of', 'vp', 'chief', 'executive'],
}

def extract_required_experience(text: str) -> float:
    text_lower = text.lower()
    for pattern in EXPERIENCE_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            return float(match.group(1))
    return 0.0

def extract_seniority(text: str) -> str:
    text_lower = text.lower()
    for level, keywords in SENIORITY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return level
    return 'mid'

def extract_skills_from_jd(text: str) -> dict:
    text_lower = text.lower()
    required = []
    preferred = []
    
    # Split into sections
    required_section = ""
    preferred_section = ""
    
    req_pattern = r'(required|must have|mandatory|essential|minimum qualifications?)(.*?)(?=preferred|nice to have|bonus|plus|desired|\Z)'
    pref_pattern = r'(preferred|nice to have|bonus|plus|desired)(.*?)(?=required|\Z)'
    
    req_match = re.search(req_pattern, text_lower, re.DOTALL)
    pref_match = re.search(pref_pattern, text_lower, re.DOTALL)
    
    required_section = req_match.group(2) if req_match else text_lower
    preferred_section = pref_match.group(2) if pref_match else ""
    
    for skill in SKILLS_DB:
        if skill in required_section:
            required.append(skill.title() if len(skill) > 3 else skill.upper())
        elif skill in preferred_section:
            preferred.append(skill.title() if len(skill) > 3 else skill.upper())
        elif not req_match and skill in text_lower:
            required.append(skill.title() if len(skill) > 3 else skill.upper())
    
    return {
        'required': list(set(required)),
        'preferred': list(set(preferred))
    }

def extract_keywords(text: str) -> list:
    try:
        tokens = word_tokenize(text.lower())
    except:
        tokens = text.lower().split()
    
    keywords = [
        word for word in tokens
        if word.isalpha() and len(word) > 3 and word not in stop_words
    ]
    
    from collections import Counter
    freq = Counter(keywords)
    return [word for word, count in freq.most_common(30)]

def extract_responsibilities(text: str) -> list:
    sentences = sent_tokenize(text) if text else []
    responsibility_keywords = [
        'will', 'responsible', 'develop', 'design', 'build', 'implement',
        'maintain', 'collaborate', 'lead', 'manage', 'create', 'work'
    ]
    responsibilities = []
    for sent in sentences:
        if any(kw in sent.lower() for kw in responsibility_keywords):
            clean = sent.strip()
            if 30 < len(clean) < 300:
                responsibilities.append(clean)
    return responsibilities[:8]

def parse_job_description(jd_text: str) -> dict:
    logger.info("Parsing job description")
    
    skills = extract_skills_from_jd(jd_text)
    
    parsed = {
        'raw_text': jd_text,
        'required_skills': skills['required'],
        'preferred_skills': skills['preferred'],
        'all_skills': list(set(skills['required'] + skills['preferred'])),
        'experience_required': extract_required_experience(jd_text),
        'seniority': extract_seniority(jd_text),
        'keywords': extract_keywords(jd_text),
        'responsibilities': extract_responsibilities(jd_text),
        'word_count': len(jd_text.split()),
    }
    
    logger.info(f"JD parsed: {len(parsed['required_skills'])} required skills, {len(parsed['preferred_skills'])} preferred skills")
    return parsed

import re
import logging
import os
import fitz  # PyMuPDF
from docx import Document
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

logger = logging.getLogger(__name__)

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt_tab', quiet=True)

SKILLS_DB = [
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust', 'scala',
    'kotlin', 'swift', 'r', 'matlab', 'php', 'perl', 'bash', 'shell', 'sql',
    # ML/AI
    'machine learning', 'deep learning', 'neural networks', 'nlp', 'computer vision',
    'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'xgboost', 'lightgbm',
    'transformers', 'bert', 'gpt', 'llm', 'reinforcement learning', 'data science',
    # Data Engineering
    'pandas', 'numpy', 'spark', 'hadoop', 'kafka', 'airflow', 'dbt', 'etl',
    'data pipeline', 'data warehouse', 'databricks', 'snowflake',
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'ci/cd', 'jenkins', 'github actions',
    'terraform', 'ansible', 'linux', 'git', 'devops', 'mlops',
    # Databases
    'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
    'dynamodb', 'oracle', 'sqlite', 'neo4j',
    # Web
    'flask', 'django', 'fastapi', 'react', 'angular', 'vue', 'node.js', 'rest api',
    'graphql', 'html', 'css', 'microservices',
    # Tools & Other
    'mlflow', 'dvc', 'wandb', 'jupyter', 'tableau', 'power bi', 'excel',
    'agile', 'scrum', 'jira', 'confluence', 'statistics', 'mathematics',
]

EDUCATION_KEYWORDS = [
    'bachelor', 'master', 'phd', 'doctorate', 'b.tech', 'm.tech', 'b.e', 'm.e',
    'b.sc', 'm.sc', 'mba', 'degree', 'university', 'college', 'institute',
    'computer science', 'engineering', 'mathematics', 'statistics', 'information technology'
]

CERT_KEYWORDS = [
    'certified', 'certification', 'aws certified', 'azure certified', 'google certified',
    'coursera', 'udemy', 'edx', 'certificate', 'credential'
]

def extract_text_from_pdf(file_path: str) -> str:
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return ""

def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        return ""

def extract_text_from_txt(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        logger.error(f"TXT extraction error: {e}")
        return ""

def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    return ""

def extract_email(text: str) -> str:
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""

def extract_phone(text: str) -> str:
    pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""

def extract_name(text: str) -> str:
    lines = text.strip().split('\n')
    for line in lines[:5]:
        line = line.strip()
        if len(line) > 2 and len(line) < 50 and not '@' in line and not any(c.isdigit() for c in line):
            if re.match(r'^[A-Za-z\s\.]+$', line):
                return line
    return "Unknown"

def extract_skills(text: str) -> list:
    text_lower = text.lower()
    found_skills = []
    for skill in SKILLS_DB:
        if skill in text_lower:
            found_skills.append(skill.title() if len(skill) > 3 else skill.upper())
    return list(set(found_skills))

def extract_experience_years(text: str) -> float:
    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience\s+of\s+(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s+of\s+experience',
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return float(match.group(1))
    
    # Try to calculate from date ranges
    year_pattern = r'(20[0-9]{2})\s*[-–]\s*(20[0-9]{2}|present|current)'
    matches = re.findall(year_pattern, text.lower())
    if matches:
        import datetime
        current_year = datetime.datetime.now().year
        total = 0
        for start, end in matches:
            end_year = current_year if end in ['present', 'current'] else int(end)
            total += max(0, end_year - int(start))
        return min(float(total), 20.0)
    return 0.0

def extract_education(text: str) -> list:
    text_lower = text.lower()
    found = []
    for keyword in EDUCATION_KEYWORDS:
        if keyword in text_lower:
            # Get surrounding context
            idx = text_lower.find(keyword)
            context = text[max(0, idx-20):min(len(text), idx+80)].strip()
            context = ' '.join(context.split())
            if context not in found:
                found.append(context)
    return found[:3]

def extract_certifications(text: str) -> list:
    text_lower = text.lower()
    certs = []
    for keyword in CERT_KEYWORDS:
        if keyword in text_lower:
            idx = text_lower.find(keyword)
            context = text[max(0, idx):min(len(text), idx+100)].strip()
            context = ' '.join(context.split())
            if context not in certs:
                certs.append(context)
    return certs[:5]

def parse_resume(file_path: str) -> dict:
    logger.info(f"Parsing resume: {file_path}")
    text = extract_text(file_path)
    
    if not text:
        return {'error': 'Could not extract text from file', 'raw_text': ''}
    
    parsed = {
        'raw_text': text,
        'name': extract_name(text),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'skills': extract_skills(text),
        'experience_years': extract_experience_years(text),
        'education': extract_education(text),
        'certifications': extract_certifications(text),
        'word_count': len(text.split()),
    }
    
    logger.info(f"Parsed resume: {len(parsed['skills'])} skills found, {parsed['experience_years']} years exp")
    return parsed

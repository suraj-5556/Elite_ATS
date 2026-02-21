import logging
import json
import os
from datetime import datetime
from typing import Dict

from app.services.resume_parser import parse_resume
from app.services.jd_parser import parse_job_description
from app.services.nlp_scorer import compute_nlp_scores
from app.services.ml_model import predict_match_score
from app.services.claude_evaluator import get_claude_evaluation

logger = logging.getLogger(__name__)

def compute_final_score(nlp_scores: Dict, ml_result: Dict, claude_eval: Dict) -> Dict:
    nlp_score = nlp_scores.get('nlp_composite_score', 0) * 100
    ml_score = ml_result.get('ml_score', 0)
    claude_score = claude_eval.get('shortlisting_score', 50)
    
    # Weighted combination
    final_score = (
        nlp_score * 0.35 +
        ml_score * 0.30 +
        claude_score * 0.35
    )
    
    final_score = round(min(100, max(0, final_score)), 1)
    
    if final_score >= 75:
        category = "Excellent Match"
        color = "#00ff88"
        shortlist = "High"
    elif final_score >= 55:
        category = "Good Match"
        color = "#ffaa00"
        shortlist = "Medium"
    elif final_score >= 35:
        category = "Partial Match"
        color = "#ff7700"
        shortlist = "Low"
    else:
        category = "Poor Match"
        color = "#ff4444"
        shortlist = "Very Low"
    
    return {
        'final_score': final_score,
        'category': category,
        'color': color,
        'shortlisting_probability': shortlist,
        'score_breakdown': {
            'nlp_score': round(nlp_score, 1),
            'ml_score': round(ml_score, 1),
            'claude_score': round(claude_score, 1),
        }
    }

def log_prediction(result: Dict):
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'final_score': result.get('final_result', {}).get('final_score'),
        'shortlisting': result.get('final_result', {}).get('shortlisting_probability'),
        'ats_score': result.get('nlp_scores', {}).get('ats_score'),
        'matched_skills': len(result.get('nlp_scores', {}).get('skill_overlap', {}).get('matched_required', [])),
        'missing_skills': len(result.get('nlp_scores', {}).get('skill_overlap', {}).get('missing_required', [])),
    }
    
    os.makedirs('logs', exist_ok=True)
    with open('logs/predictions.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def run_full_matching(file_path: str, jd_text: str) -> Dict:
    logger.info("Starting full resume-JD matching pipeline")
    
    try:
        # Step 1: Parse
        resume_data = parse_resume(file_path)
        if 'error' in resume_data:
            return {'error': resume_data['error']}
        
        jd_data = parse_job_description(jd_text)
        
        # Step 2: NLP Scores
        nlp_scores = compute_nlp_scores(resume_data, jd_data)
        
        # Step 3: ML Prediction
        ml_result = predict_match_score(nlp_scores)
        
        # Step 4: Claude Evaluation
        claude_eval = get_claude_evaluation(resume_data, jd_data, nlp_scores)
        
        # Step 5: Final Score
        final_result = compute_final_score(nlp_scores, ml_result, claude_eval)
        
        result = {
            'resume': {
                'name': resume_data.get('name', 'Unknown'),
                'email': resume_data.get('email', ''),
                'skills': resume_data.get('skills', []),
                'experience_years': resume_data.get('experience_years', 0),
                'education': resume_data.get('education', []),
                'certifications': resume_data.get('certifications', []),
            },
            'job': {
                'required_skills': jd_data.get('required_skills', []),
                'preferred_skills': jd_data.get('preferred_skills', []),
                'experience_required': jd_data.get('experience_required', 0),
                'seniority': jd_data.get('seniority', 'mid'),
            },
            'nlp_scores': nlp_scores,
            'ml_result': ml_result,
            'claude_eval': claude_eval,
            'final_result': final_result,
        }
        
        log_prediction(result)
        logger.info(f"Matching complete. Final score: {final_result['final_score']}%")
        return result
        
    except Exception as e:
        logger.error(f"Matching pipeline error: {e}", exc_info=True)
        return {'error': str(e)}

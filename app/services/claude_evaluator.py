import os
import logging
import json
import anthropic
from typing import Dict

logger = logging.getLogger(__name__)

def get_claude_evaluation(resume_data: Dict, jd_data: Dict, nlp_scores: Dict) -> Dict:
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    
    if not api_key:
        logger.warning("No Anthropic API key found, using mock evaluation")
        return _mock_evaluation(resume_data, jd_data, nlp_scores)
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        skill_overlap = nlp_scores.get('skill_overlap', {})
        
        prompt = f"""You are an expert technical recruiter and HR specialist. Analyze this resume against the job description and provide a structured evaluation.

RESUME SUMMARY:
- Skills: {', '.join(resume_data.get('skills', [])[:20])}
- Experience: {resume_data.get('experience_years', 0)} years
- Education: {'; '.join(resume_data.get('education', [])[:2])}
- Certifications: {len(resume_data.get('certifications', []))} found

JOB DESCRIPTION SUMMARY:
- Required Skills: {', '.join(jd_data.get('required_skills', [])[:15])}
- Preferred Skills: {', '.join(jd_data.get('preferred_skills', [])[:10])}
- Experience Required: {jd_data.get('experience_required', 0)} years
- Seniority: {jd_data.get('seniority', 'mid')}

NLP ANALYSIS:
- Skill Match: {skill_overlap.get('required_score', 0)*100:.1f}% of required skills matched
- Matched Skills: {', '.join(skill_overlap.get('matched_required', [])[:10])}
- Missing Skills: {', '.join(skill_overlap.get('missing_required', [])[:10])}
- TF-IDF Similarity: {nlp_scores.get('tfidf_similarity', 0)*100:.1f}%

Provide your evaluation as a JSON object with these exact fields:
{{
  "shortlisting_probability": "High|Medium|Low",
  "shortlisting_score": <number 0-100>,
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2", "weakness3"],
  "missing_critical_skills": ["skill1", "skill2"],
  "improvement_suggestions": ["suggestion1", "suggestion2", "suggestion3", "suggestion4"],
  "interview_likelihood": "Very Likely|Likely|Unlikely|Very Unlikely",
  "overall_assessment": "<2-3 sentence summary>",
  "recommended_action": "Apply Confidently|Apply with Improvements|Significant Gaps|Not Recommended"
}}

Return ONLY the JSON object, no additional text."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        
        # Clean JSON if wrapped in markdown
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        evaluation = json.loads(response_text)
        evaluation['source'] = 'claude'
        
        logger.info(f"Claude evaluation: {evaluation.get('shortlisting_probability')} probability")
        return evaluation
        
    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        return _mock_evaluation(resume_data, jd_data, nlp_scores)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error from Claude: {e}")
        return _mock_evaluation(resume_data, jd_data, nlp_scores)
    except Exception as e:
        logger.error(f"Claude evaluation error: {e}")
        return _mock_evaluation(resume_data, jd_data, nlp_scores)

def _mock_evaluation(resume_data: Dict, jd_data: Dict, nlp_scores: Dict) -> Dict:
    """Fallback evaluation when Claude API is unavailable"""
    skill_overlap = nlp_scores.get('skill_overlap', {})
    req_score = skill_overlap.get('required_score', 0)
    matched = skill_overlap.get('matched_required', [])
    missing = skill_overlap.get('missing_required', [])
    
    if req_score >= 0.7:
        prob = "High"
        score = int(70 + req_score * 30)
        action = "Apply Confidently"
        interview = "Very Likely"
    elif req_score >= 0.45:
        prob = "Medium"
        score = int(45 + req_score * 40)
        action = "Apply with Improvements"
        interview = "Likely"
    else:
        prob = "Low"
        score = int(req_score * 60)
        action = "Significant Gaps"
        interview = "Unlikely"
    
    strengths = []
    if matched:
        strengths.append(f"Strong match on core skills: {', '.join(matched[:3])}")
    if resume_data.get('experience_years', 0) >= jd_data.get('experience_required', 0):
        strengths.append("Meets experience requirements")
    if resume_data.get('certifications'):
        strengths.append("Has relevant certifications")
    if not strengths:
        strengths = ["Has some transferable skills"]
    
    suggestions = []
    if missing:
        suggestions.append(f"Learn missing skills: {', '.join(list(missing)[:3])}")
    suggestions.append("Add measurable achievements with quantified impact")
    suggestions.append("Include relevant project experience and outcomes")
    suggestions.append("Tailor resume keywords to match job description")
    
    return {
        'shortlisting_probability': prob,
        'shortlisting_score': score,
        'strengths': strengths,
        'weaknesses': [f"Missing: {s}" for s in list(missing)[:2]] or ["Limited skill overlap"],
        'missing_critical_skills': list(missing)[:5],
        'improvement_suggestions': suggestions,
        'interview_likelihood': interview,
        'overall_assessment': f"Candidate matches approximately {req_score*100:.0f}% of required skills. {'Strong candidate for this role.' if prob == 'High' else 'Candidate should address skill gaps before applying.' if prob == 'Low' else 'Candidate shows potential but has room for improvement.'}",
        'recommended_action': action,
        'source': 'mock',
    }

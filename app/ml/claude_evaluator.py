"""
Claude AI Evaluator: Uses Anthropic's Claude to perform deep semantic evaluation
of resume vs. job description. Returns structured JSON with scores and insights.
Weight in final score: 35%

Falls back to rule-based evaluator if Claude API is unavailable.
"""

import os
import json
import logging
import re

logger = logging.getLogger(__name__)


CLAUDE_SYSTEM_PROMPT = """You are an expert AI recruitment specialist and resume screener with 15+ years of experience.
You evaluate resumes against job descriptions with precision and fairness.

Always respond in valid JSON only. No markdown, no explanations outside the JSON."""

CLAUDE_USER_TEMPLATE = """Evaluate this resume against the job description and return ONLY a JSON object.

JOB DESCRIPTION:
{jd}

RESUME:
{resume}

Return this exact JSON structure:
{{
  "score": <number 0-100, overall fit score>,
  "strengths": [<list of 3 specific strengths matching the JD>],
  "weaknesses": [<list of 2-3 specific gaps or weaknesses>],
  "suggestions": [<list of 3 actionable improvement suggestions>],
  "shortlisting_rationale": "<1-2 sentence justification for your score>",
  "experience_match": <number 0-100>,
  "skills_match": <number 0-100>,
  "cultural_fit": <number 0-100>
}}"""


def evaluate_with_claude(resume_text: str, jd_text: str) -> dict:
    """
    Call Claude API to evaluate resume. Falls back to rule-based on any error.
    Returns dict with score, strengths, weaknesses, suggestions.
    """
    api_key = os.getenv('ANTHROPIC_API_KEY', '')

    if not api_key or api_key.startswith('sk-ant-your'):
        logger.info("No valid Claude API key. Using rule-based evaluator.")
        return _rule_based_evaluator(resume_text, jd_text)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        # Truncate to avoid token limits
        resume_truncated = resume_text[:4000]
        jd_truncated = jd_text[:2000]

        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=CLAUDE_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": CLAUDE_USER_TEMPLATE.format(
                    jd=jd_truncated,
                    resume=resume_truncated
                )
            }]
        )

        response_text = message.content[0].text.strip()

        # Strip any accidental markdown fences
        response_text = re.sub(r'^```json\s*', '', response_text)
        response_text = re.sub(r'\s*```$', '', response_text)

        result = json.loads(response_text)

        # Validate and normalize
        score = float(result.get('score', 0))
        score = max(0, min(100, score))

        return {
            'score': round(score, 2),
            'strengths': result.get('strengths', [])[:3],
            'weaknesses': result.get('weaknesses', [])[:3],
            'suggestions': result.get('suggestions', [])[:3],
            'shortlisting_rationale': result.get('shortlisting_rationale', ''),
            'experience_match': float(result.get('experience_match', score)),
            'skills_match': float(result.get('skills_match', score)),
            'cultural_fit': float(result.get('cultural_fit', 50)),
            'source': 'claude',
        }

    except json.JSONDecodeError as e:
        logger.error(f"Claude returned invalid JSON: {e}")
        return _rule_based_evaluator(resume_text, jd_text)
    except Exception as e:
        logger.error(f"Claude API error: {e}. Falling back to rule-based.")
        return _rule_based_evaluator(resume_text, jd_text)


def _rule_based_evaluator(resume_text: str, jd_text: str) -> dict:
    """
    Fallback evaluator that uses heuristics when Claude is unavailable.
    Ensures the system works in offline/demo mode.
    """
    r = resume_text.lower()
    j = jd_text.lower()

    # Extract key JD terms (nouns/tech words longer than 3 chars)
    jd_terms = set(re.findall(r'\b[a-z][a-z0-9+#.]{3,}\b', j))
    stop_words = {
        'with', 'will', 'have', 'this', 'that', 'from', 'they', 'been',
        'experience', 'looking', 'seeking', 'required', 'preferred', 'skills'
    }
    jd_terms -= stop_words

    matched = [t for t in jd_terms if t in r]
    match_ratio = len(matched) / max(len(jd_terms), 1)
    base_score = match_ratio * 100

    # Boost for quantified achievements
    if re.search(r'\d+%|\d+ years|\$\d+', resume_text):
        base_score = min(base_score + 8, 100)

    # Boost for strong sections
    if all(s in r for s in ['experience', 'education', 'skills']):
        base_score = min(base_score + 5, 100)

    score = round(base_score, 2)

    # Generate contextual suggestions
    suggestions = []
    if match_ratio < 0.4:
        suggestions.append("Tailor your resume keywords to closely match the job description language.")
    if not re.search(r'\d+%|\d+ years|\$\d+', resume_text):
        suggestions.append("Add quantified achievements (e.g., 'increased performance by 30%').")
    if 'github' not in r and 'portfolio' not in r:
        suggestions.append("Include a link to your GitHub profile or portfolio projects.")
    if len(suggestions) == 0:
        suggestions.append("Consider adding industry certifications relevant to this role.")

    strengths = []
    if match_ratio > 0.5:
        strengths.append("Strong keyword alignment with the job description.")
    if len(resume_text.split()) > 400:
        strengths.append("Well-detailed resume with comprehensive content.")
    if re.search(r'\d+%|\d+ years', resume_text):
        strengths.append("Includes quantified achievements demonstrating impact.")
    if not strengths:
        strengths.append("Resume covers required experience areas.")

    weaknesses = []
    if match_ratio < 0.3:
        weaknesses.append("Limited keyword match with job requirements.")
    if len(resume_text.split()) < 300:
        weaknesses.append("Resume may be too brief; consider expanding key sections.")
    if not weaknesses:
        weaknesses.append("Could better highlight leadership and collaboration experience.")

    return {
        'score': score,
        'strengths': strengths[:3],
        'weaknesses': weaknesses[:2],
        'suggestions': suggestions[:3],
        'shortlisting_rationale': (
            f"Resume matches approximately {round(match_ratio * 100)}% of job requirements. "
            "Score based on keyword alignment and resume quality metrics."
        ),
        'experience_match': min(score + 5, 100),
        'skills_match': round(match_ratio * 100, 2),
        'cultural_fit': 60.0,
        'source': 'rule_based',
    }

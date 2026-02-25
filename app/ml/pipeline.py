"""
AI Screening Pipeline Orchestrator.
Coordinates all scoring components and produces the final composite score.

Architecture Decision: Pipeline pattern keeps each scorer independent,
making it easy to swap/upgrade individual components without touching others.

Final Score Formula:
  final_score = (nlp_score * 0.35) + (ml_score * 0.30) + (claude_score * 0.35)
"""

import time
import logging
from datetime import datetime, timezone
from typing import Optional

from .resume_parser import parse_resume
from .nlp_scorer import compute_nlp_score, extract_skills
from .ml_scorer import compute_ml_score, compute_ats_score
from .claude_evaluator import evaluate_with_claude

logger = logging.getLogger(__name__)

# Score weights (must sum to 1.0)
NLP_WEIGHT = 0.35
ML_WEIGHT = 0.30
CLAUDE_WEIGHT = 0.35


def run_screening_pipeline(
    file_bytes: bytes,
    filename: str,
    jd_text: str,
    user_id: str,
) -> dict:
    """
    Full screening pipeline. Returns a result dict ready to store in MongoDB.
    
    Args:
        file_bytes: Raw bytes of the uploaded resume file
        filename: Original filename (used to determine file type)
        jd_text: Job description text
        user_id: ID of the uploading user
    
    Returns:
        Complete analysis result dict
    """
    pipeline_start = time.time()
    logger.info(f"Starting screening pipeline for user {user_id}, file: {filename}")

    # ── Step 1: Parse Resume ──────────────────────────────────────────────────
    t0 = time.time()
    resume_text = parse_resume(file_bytes, filename)
    parse_time = time.time() - t0

    if not resume_text or len(resume_text.strip()) < 50:
        raise ValueError("Could not extract meaningful text from the uploaded file. "
                        "Please ensure the file is not empty or scanned image-only.")

    logger.info(f"Resume parsed: {len(resume_text)} chars in {parse_time:.2f}s")

    # ── Step 2: NLP Score (TF-IDF Cosine) ────────────────────────────────────
    t0 = time.time()
    nlp_score = compute_nlp_score(resume_text, jd_text)
    nlp_time = time.time() - t0
    logger.info(f"NLP score: {nlp_score:.1f} in {nlp_time:.2f}s")

    # ── Step 3: Extract Skills ────────────────────────────────────────────────
    matched_skills, missing_skills = extract_skills(resume_text, jd_text)

    # ── Step 4: ML Score (Gradient Boosting) ─────────────────────────────────
    t0 = time.time()
    ml_score, model_version = compute_ml_score(resume_text, jd_text)
    ml_time = time.time() - t0
    logger.info(f"ML score: {ml_score:.1f} (model: {model_version}) in {ml_time:.2f}s")

    # ── Step 5: ATS Score ─────────────────────────────────────────────────────
    ats_score = compute_ats_score(resume_text, jd_text)

    # ── Step 6: Claude AI Score ───────────────────────────────────────────────
    t0 = time.time()
    claude_result = evaluate_with_claude(resume_text, jd_text)
    claude_score = claude_result['score']
    claude_time = time.time() - t0
    logger.info(f"Claude score: {claude_score:.1f} (source: {claude_result['source']}) in {claude_time:.2f}s")

    # ── Step 7: Composite Final Score ─────────────────────────────────────────
    final_score = (
        nlp_score * NLP_WEIGHT +
        ml_score * ML_WEIGHT +
        claude_score * CLAUDE_WEIGHT
    )
    final_score = round(min(max(final_score, 0), 100), 2)

    # ── Step 8: Shortlisting Probability ──────────────────────────────────────
    # Sigmoid-like scaling: scores above 70 get higher probability
    shortlisting_probability = _compute_shortlisting_probability(final_score)

    total_time = time.time() - pipeline_start
    logger.info(f"Pipeline complete. Final score: {final_score:.1f}, Time: {total_time:.2f}s")

    # ── MLflow Logging ────────────────────────────────────────────────────────
    try:
        _log_to_mlflow(
            user_id=user_id,
            filename=filename,
            nlp_score=nlp_score,
            ml_score=ml_score,
            claude_score=claude_score,
            final_score=final_score,
            model_version=model_version,
            latency=total_time,
        )
    except Exception as e:
        logger.warning(f"MLflow logging failed (non-critical): {e}")

    return {
        'user_id': user_id,
        'filename': filename,
        'resume_text': resume_text,
        'job_description': jd_text,
        'nlp_score': nlp_score,
        'ml_score': ml_score,
        'claude_score': claude_score,
        'final_score': final_score,
        'ats_score': ats_score,
        'shortlisting_probability': shortlisting_probability,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'improvement_suggestions': claude_result.get('suggestions', []),
        'strengths': claude_result.get('strengths', []),
        'weaknesses': claude_result.get('weaknesses', []),
        'shortlisting_rationale': claude_result.get('shortlisting_rationale', ''),
        'evaluator_source': claude_result.get('source', 'unknown'),
        'uploaded_at': datetime.now(timezone.utc),
        'model_version': model_version,
        'pipeline_latency_ms': round(total_time * 1000, 0),
    }


def _compute_shortlisting_probability(final_score: float) -> float:
    """
    Map final score (0-100) to shortlisting probability (0-1).
    Uses a smooth sigmoid-like curve.
    """
    import math
    # Center at 65, steep slope
    x = (final_score - 65) / 10
    prob = 1 / (1 + math.exp(-x))
    return round(prob, 3)


def _log_to_mlflow(
    user_id: str,
    filename: str,
    nlp_score: float,
    ml_score: float,
    claude_score: float,
    final_score: float,
    model_version: str,
    latency: float,
) -> None:
    """Log prediction metrics to MLflow for model monitoring."""
    import mlflow
    import os

    tracking_uri = os.getenv('MLFLOW_TRACKING_URI', './mlruns')
    experiment_name = os.getenv('MLFLOW_EXPERIMENT_NAME', 'talentai-resume-screening')

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name=f"inference_{model_version}"):
        mlflow.log_metrics({
            'nlp_score': nlp_score,
            'ml_score': ml_score,
            'claude_score': claude_score,
            'final_score': final_score,
            'latency_seconds': latency,
        })
        mlflow.log_params({
            'model_version': model_version,
            'nlp_weight': NLP_WEIGHT,
            'ml_weight': ML_WEIGHT,
            'claude_weight': CLAUDE_WEIGHT,
        })

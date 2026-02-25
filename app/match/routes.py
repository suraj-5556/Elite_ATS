"""
Match routes: Resume upload, analysis, and results.
Handles file validation, pipeline execution, and result storage.
"""

import os
import uuid
import logging
from werkzeug.utils import secure_filename
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.match import match_bp
from app.database import get_db
from app.ml.pipeline import run_screening_pipeline

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_JD_LENGTH = 5000


def _allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@match_bp.route('/', methods=['GET'])
@login_required
def index():
    """Resume upload form."""
    from ..jobs.routes import SAMPLE_JOBS
    return render_template('match/index.html', jobs=SAMPLE_JOBS)


@match_bp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    """
    Handle resume upload + JD submission.
    Validates inputs, runs pipeline, stores result, redirects to results page.
    """
    # ── Input Validation ──────────────────────────────────────────────────────
    if 'resume' not in request.files:
        flash('No file uploaded. Please select a resume file.', 'error')
        return redirect(url_for('match.index'))

    file = request.files['resume']
    jd_text = request.form.get('job_description', '').strip()

    if not file or file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('match.index'))

    if not _allowed_file(file.filename):
        flash('Invalid file type. Please upload PDF, DOCX, or TXT.', 'error')
        return redirect(url_for('match.index'))

    if not jd_text or len(jd_text) < 50:
        flash('Job description must be at least 50 characters.', 'error')
        return redirect(url_for('match.index'))

    if len(jd_text) > MAX_JD_LENGTH:
        jd_text = jd_text[:MAX_JD_LENGTH]

    # ── Read File Bytes ───────────────────────────────────────────────────────
    file_bytes = file.read()
    if len(file_bytes) > 10 * 1024 * 1024:  # 10MB
        flash('File too large. Maximum size is 10MB.', 'error')
        return redirect(url_for('match.index'))

    safe_filename = secure_filename(file.filename)

    # ── Run Pipeline ──────────────────────────────────────────────────────────
    try:
        result = run_screening_pipeline(
            file_bytes=file_bytes,
            filename=safe_filename,
            jd_text=jd_text,
            user_id=current_user.id,
        )
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('match.index'))
    except Exception as e:
        logger.error(f"Pipeline error for user {current_user.id}: {e}", exc_info=True)
        flash('Analysis failed. Please try again with a different file.', 'error')
        return redirect(url_for('match.index'))

    # ── Store in MongoDB ──────────────────────────────────────────────────────
    db = get_db()
    insert_result = db.resumes.insert_one(result)
    resume_id = str(insert_result.inserted_id)

    logger.info(f"Analysis complete for user {current_user.id}. Resume ID: {resume_id}")
    return redirect(url_for('match.results', resume_id=resume_id))


@match_bp.route('/results/<resume_id>')
@login_required
def results(resume_id: str):
    """Display analysis results. Only the owner can view their results."""
    from bson import ObjectId
    db = get_db()

    resume = db.resumes.find_one({
        '_id': ObjectId(resume_id),
        'user_id': current_user.id,  # ← Security: ownership check
    })

    if not resume:
        flash('Analysis not found or access denied.', 'error')
        return redirect(url_for('match.index'))

    resume['_id'] = str(resume['_id'])
    return render_template('match/results.html', resume=resume)

"""
Dashboard routes: personal analytics, resume history, delete.
All routes are protected by login_required.
Security: users can only see/delete their own resumes (enforced by user_id filter).
"""

import logging
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from bson import ObjectId
from app.dashboard import dashboard_bp
from app.database import get_db

logger = logging.getLogger(__name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    db = get_db()
    resumes = list(
        db.resumes.find(
            {'user_id': current_user.id},
            sort=[('uploaded_at', -1)]
        ).limit(50)
    )

    # ── Compute aggregate stats ───────────────────────────────────────────────
    total = len(resumes)
    avg_score = round(sum(r.get('final_score', 0) for r in resumes) / total, 1) if total else 0
    shortlisted = sum(1 for r in resumes if r.get('shortlisting_probability', 0) >= 0.6)
    last_resume = resumes[0] if resumes else None

    # Serialize ObjectIds for template
    for r in resumes:
        r['_id'] = str(r['_id'])

    return render_template(
        'dashboard/index.html',
        resumes=resumes,
        total=total,
        avg_score=avg_score,
        shortlisted=shortlisted,
        last_resume=last_resume,
    )


@dashboard_bp.route('/dashboard/stats')
@login_required
def stats():
    """JSON endpoint for dashboard charts (called via Fetch API)."""
    db = get_db()
    resumes = list(db.resumes.find(
        {'user_id': current_user.id},
        {'final_score': 1, 'nlp_score': 1, 'ml_score': 1, 'claude_score': 1, 'uploaded_at': 1}
    ).sort('uploaded_at', 1).limit(20))

    data = [{
        'date': r['uploaded_at'].strftime('%b %d') if r.get('uploaded_at') else 'N/A',
        'final': round(r.get('final_score', 0), 1),
        'nlp': round(r.get('nlp_score', 0), 1),
        'ml': round(r.get('ml_score', 0), 1),
        'claude': round(r.get('claude_score', 0), 1),
    } for r in resumes]

    return jsonify({'scores': data})


@dashboard_bp.route('/dashboard/delete/<resume_id>', methods=['POST'])
@login_required
def delete_resume(resume_id: str):
    """Delete a resume. Only the owner can delete."""
    db = get_db()
    result = db.resumes.delete_one({
        '_id': ObjectId(resume_id),
        'user_id': current_user.id,  # ← Security: ownership check
    })

    if result.deleted_count:
        flash('Resume deleted successfully.', 'success')
    else:
        flash('Resume not found or access denied.', 'error')

    return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/my-resumes')
@login_required
def my_resumes():
    db = get_db()
    resumes = list(
        db.resumes.find({'user_id': current_user.id}).sort('uploaded_at', -1)
    )
    for r in resumes:
        r['_id'] = str(r['_id'])
    return render_template('dashboard/my_resumes.html', resumes=resumes)

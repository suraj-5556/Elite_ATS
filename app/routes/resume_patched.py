"""
app/routes/resume.py  — patched version
Saves uploaded PDF binary to MongoDB alongside the parsed data.
"""
import os
import datetime
from flask import Blueprint, request, jsonify, session, current_app
from app.db import get_db

resume_bp = Blueprint('resume', __name__, url_prefix='/resume')

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}


def _allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@resume_bp.route('/upload', methods=['POST'])
def upload():
    """Upload a resume, parse it, and (if user is logged-in) persist to MongoDB."""
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['resume']
    if not file or not _allowed(file.filename):
        return jsonify({'error': 'Invalid file type. Use PDF, DOCX, or TXT.'}), 400

    file_bytes = file.read()
    filename   = file.filename
    ext        = filename.rsplit('.', 1)[1].lower()

    # ── Parse ─────────────────────────────────────────────────────────────────
    try:
        from app.services.resume_parser import ResumeParser
        parser  = ResumeParser()
        content = parser.parse_bytes(file_bytes, ext)   # returns dict
    except Exception as exc:
        current_app.logger.error(f'Resume parse error: {exc}')
        return jsonify({'error': 'Failed to parse resume.'}), 500

    # ── Persist to MongoDB (only for logged-in users) ─────────────────────────
    if 'user_id' in session:
        db     = get_db()
        doc    = {
            'user_id':     session['user_id'],
            'filename':    filename,
            'pdf_data':    file_bytes if ext == 'pdf' else None,
            'parsed':      content,
            'uploaded_at': datetime.datetime.utcnow(),
        }
        result = db['resumes'].insert_one(doc)
        content['resume_id'] = str(result.inserted_id)

    # ── Store in session for analysis pipeline ────────────────────────────────
    session['resume_data'] = content

    return jsonify({'success': True, 'data': content})

import os
from flask import Blueprint, request, jsonify, render_template, current_app
from werkzeug.utils import secure_filename
import uuid

match_bp = Blueprint('match', __name__)

@match_bp.route('/')
def match_page():
    return render_template('match.html')

@match_bp.route('/analyze', methods=['POST'])
def analyze():
    from app.services.matcher import run_full_matching
    
    jd_text = request.form.get('jd_text', '').strip()
    
    if not jd_text:
        return jsonify({'error': 'Job description is required'}), 400
    
    if len(jd_text) < 50:
        return jsonify({'error': 'Job description too short (min 50 characters)'}), 400
    
    if 'resume' not in request.files:
        return jsonify({'error': 'Resume file is required'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No resume file selected'}), 400
    
    allowed = {'pdf', 'docx', 'txt'}
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in allowed:
        return jsonify({'error': f'Invalid file type: {ext}. Use PDF, DOCX, or TXT'}), 400
    
    filename = f"{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    try:
        result = run_full_matching(file_path, jd_text)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
    finally:
        # Clean up uploaded file after analysis
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

@match_bp.route('/results')
def results_page():
    return render_template('results.html')

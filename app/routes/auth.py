from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from app.db import get_db
import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# ─── Login Required Decorator ────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# ─── Register ────────────────────────────────────────────────────────────────

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        db    = get_db()
        users = db['users']

        if not all([name, email, password, confirm]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/register.html')

        if users.find_one({'email': email}):
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        user = {
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'created_at': datetime.datetime.utcnow(),
        }
        result = users.insert_one(user)

        session['user_id']    = str(result.inserted_id)
        session['user_name']  = name
        session['user_email'] = email

        flash(f'Welcome, {name}! Account created.', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/register.html')


# ─── Login ────────────────────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        db   = get_db()
        user = db['users'].find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            session['user_id']    = str(user['_id'])
            session['user_name']  = user['name']
            session['user_email'] = user['email']
            flash(f'Welcome back, {user["name"]}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))

        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')


# ─── Logout ───────────────────────────────────────────────────────────────────

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


# ─── Profile / My Resumes ─────────────────────────────────────────────────────

@auth_bp.route('/profile')
@login_required
def profile():
    db      = get_db()
    resumes = list(db['resumes'].find({'user_id': session['user_id']}).sort('uploaded_at', -1))
    # Convert binary to flag only (don't send raw bytes to template)
    for r in resumes:
        r['has_pdf'] = bool(r.get('pdf_data'))
        r.pop('pdf_data', None)
    return render_template('auth/profile.html', resumes=resumes)


# ─── Download Resume PDF ──────────────────────────────────────────────────────

@auth_bp.route('/resume/<resume_id>/download')
@login_required
def download_resume(resume_id):
    from bson import ObjectId
    from flask import send_file, abort
    import io

    db     = get_db()
    resume = db['resumes'].find_one({'_id': ObjectId(resume_id), 'user_id': session['user_id']})

    if not resume or not resume.get('pdf_data'):
        abort(404)

    return send_file(
        io.BytesIO(resume['pdf_data']),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=resume.get('filename', 'resume.pdf')
    )


# ─── Delete Resume ────────────────────────────────────────────────────────────

@auth_bp.route('/resume/<resume_id>/delete', methods=['POST'])
@login_required
def delete_resume(resume_id):
    from bson import ObjectId
    db = get_db()
    db['resumes'].delete_one({'_id': ObjectId(resume_id), 'user_id': session['user_id']})
    flash('Resume deleted.', 'info')
    return redirect(url_for('auth.profile'))

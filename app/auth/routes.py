"""
Authentication routes: register, login, logout.
Passwords are hashed with Werkzeug's PBKDF2-SHA256.
"""

import re
import logging
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.auth import auth_bp
from app.models import User

logger = logging.getLogger(__name__)
EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        errors = []
        if not name or len(name) < 2:
            errors.append('Name must be at least 2 characters.')
        if not EMAIL_RE.match(email):
            errors.append('Invalid email address.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('auth/register.html', name=name, email=email)

        if User.find_by_email(email):
            flash('An account with that email already exists.', 'error')
            return render_template('auth/register.html', name=name, email=email)

        hashed = generate_password_hash(password)
        user = User.create(name=name, email=email, password_hash=hashed)

        if not user:
            flash('Registration failed. Please try again.', 'error')
            return render_template('auth/register.html', name=name, email=email)

        login_user(user)
        flash(f'Welcome to TalentAI, {user.name}! 🎉', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.find_by_email(email)

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password.', 'error')
            return render_template('auth/login.html', email=email)

        login_user(user, remember=remember)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard.index'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

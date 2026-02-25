/**
 * TalentAI - Auth Form Validation
 * Client-side validation for login and register forms.
 * Backend validation is the source of truth; this is UX improvement only.
 */

"use strict";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

function showError(fieldId, message) {
  const el = document.getElementById(fieldId + 'Error');
  const input = document.getElementById(fieldId);
  if (el) el.textContent = message;
  if (input) input.classList.toggle('error', !!message);
}

function clearError(fieldId) {
  showError(fieldId, '');
}

// ── Password strength indicator ────────────────────────────────
const pwInput = document.getElementById('password');
const pwStrength = document.getElementById('pwStrength');

if (pwInput && pwStrength) {
  pwInput.addEventListener('input', () => {
    const val = pwInput.value;
    let strength = 0;
    if (val.length >= 8) strength++;
    if (/[A-Z]/.test(val)) strength++;
    if (/[0-9]/.test(val)) strength++;
    if (/[^a-zA-Z0-9]/.test(val)) strength++;

    const labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];
    const classes = ['', 'pw-weak', 'pw-fair', 'pw-strong', 'pw-strong'];
    pwStrength.textContent = val.length > 0 ? `Password strength: ${labels[strength]}` : '';
    pwStrength.className = 'password-strength ' + (classes[strength] || '');
  });
}

// ── Register form ──────────────────────────────────────────────
const registerForm = document.getElementById('registerForm');
if (registerForm) {
  registerForm.addEventListener('submit', (e) => {
    let valid = true;

    const name = document.getElementById('name')?.value.trim();
    const email = document.getElementById('email')?.value.trim();
    const password = document.getElementById('password')?.value;
    const confirm = document.getElementById('confirm_password')?.value;

    if (!name || name.length < 2) {
      showError('name', 'Name must be at least 2 characters.');
      valid = false;
    } else clearError('name');

    if (!EMAIL_RE.test(email)) {
      showError('email', 'Please enter a valid email address.');
      valid = false;
    } else clearError('email');

    if (password.length < 8) {
      showError('password', 'Password must be at least 8 characters.');
      valid = false;
    } else clearError('password');

    if (password !== confirm) {
      showError('confirm', 'Passwords do not match.');
      valid = false;
    } else clearError('confirm');

    if (!valid) {
      e.preventDefault();
      return;
    }

    // Show loading state
    const btn = document.getElementById('submitBtn');
    if (btn) {
      btn.querySelector('.btn-text').style.display = 'none';
      btn.querySelector('.btn-loader').style.display = 'inline';
      btn.disabled = true;
    }
  });
}

// ── Login form ─────────────────────────────────────────────────
const loginForm = document.getElementById('loginForm');
if (loginForm) {
  loginForm.addEventListener('submit', (e) => {
    let valid = true;

    const email = document.getElementById('email')?.value.trim();
    const password = document.getElementById('password')?.value;

    if (!EMAIL_RE.test(email)) {
      showError('email', 'Please enter a valid email address.');
      valid = false;
    } else clearError('email');

    if (!password || password.length < 1) {
      showError('password', 'Please enter your password.');
      valid = false;
    } else clearError('password');

    if (!valid) {
      e.preventDefault();
      return;
    }

    const btn = document.getElementById('submitBtn');
    if (btn) {
      btn.querySelector('.btn-text').style.display = 'none';
      btn.querySelector('.btn-loader').style.display = 'inline';
      btn.disabled = true;
    }
  });
}

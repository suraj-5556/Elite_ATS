/**
 * TalentAI - Match Page JavaScript
 * Handles:
 * - Drag & drop file upload zone
 * - File validation
 * - JD character counter
 * - Progress bar animation during submission
 * - Form validation
 */

"use strict";

const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('resumeFile');
const uploadPreview = document.getElementById('uploadPreview');
const previewName = document.getElementById('previewName');
const previewSize = document.getElementById('previewSize');
const fileError = document.getElementById('fileError');

const ALLOWED_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
const ALLOWED_EXT = ['.pdf', '.docx', '.txt'];
const MAX_SIZE = 10 * 1024 * 1024; // 10MB

// ── Click to browse ────────────────────────────────────────────
if (uploadZone) {
  uploadZone.addEventListener('click', (e) => {
    if (e.target.tagName !== 'BUTTON') fileInput.click();
  });
}

// ── Drag & Drop ────────────────────────────────────────────────
['dragenter', 'dragover'].forEach(event => {
  uploadZone?.addEventListener(event, (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
  });
});

['dragleave', 'drop'].forEach(event => {
  uploadZone?.addEventListener(event, (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
  });
});

uploadZone?.addEventListener('drop', (e) => {
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    fileInput.files = files;
    handleFileSelected(files[0]);
  }
});

// ── File input change ──────────────────────────────────────────
fileInput?.addEventListener('change', () => {
  if (fileInput.files.length > 0) {
    handleFileSelected(fileInput.files[0]);
  }
});

function handleFileSelected(file) {
  // Validate extension
  const ext = '.' + file.name.split('.').pop().toLowerCase();
  if (!ALLOWED_EXT.includes(ext)) {
    fileError.textContent = 'Invalid file type. Please upload PDF, DOCX, or TXT.';
    resetUploadZone();
    return;
  }

  // Validate size
  if (file.size > MAX_SIZE) {
    fileError.textContent = 'File too large. Maximum size is 10MB.';
    resetUploadZone();
    return;
  }

  fileError.textContent = '';
  showFilePreview(file);
}

function showFilePreview(file) {
  const uploadContent = uploadZone.querySelector('.upload-icon, .upload-text');
  if (uploadContent) uploadContent.style.display = 'none';

  // Hide upload icon and text divs
  uploadZone.querySelectorAll('.upload-icon, .upload-text').forEach(el => el.style.display = 'none');

  previewName.textContent = file.name;
  previewSize.textContent = formatFileSize(file.size);
  uploadPreview.style.display = 'flex';
}

function resetUploadZone() {
  fileInput.value = '';
  uploadPreview.style.display = 'none';
  uploadZone.querySelectorAll('.upload-icon, .upload-text').forEach(el => el.style.display = '');
}

// ── JD character counter ───────────────────────────────────────
const jdTextarea = document.getElementById('job_description');
const jdCharCount = document.getElementById('jdCharCount');

if (jdTextarea && jdCharCount) {
  const update = () => jdCharCount.textContent = jdTextarea.value.length;
  jdTextarea.addEventListener('input', update);
  update(); // init
}

// ── Form submission with progress ─────────────────────────────
const matchForm = document.getElementById('matchForm');
const analyzeBtn = document.getElementById('analyzeBtn');
const uploadProgress = document.getElementById('uploadProgress');
const progressFill = document.getElementById('progressFill');
const steps = document.querySelectorAll('.progress-steps .step');

if (matchForm) {
  matchForm.addEventListener('submit', (e) => {
    // Validate file
    if (!fileInput.files || fileInput.files.length === 0) {
      e.preventDefault();
      fileError.textContent = 'Please select a resume file.';
      return;
    }

    // Validate JD
    const jdVal = jdTextarea?.value.trim();
    const jdErr = document.getElementById('jdError');
    if (!jdVal || jdVal.length < 50) {
      e.preventDefault();
      if (jdErr) jdErr.textContent = 'Job description must be at least 50 characters.';
      return;
    }
    if (jdErr) jdErr.textContent = '';

    // Show loading UI
    analyzeBtn.querySelector('.btn-text').style.display = 'none';
    analyzeBtn.querySelector('.btn-loader').style.display = 'inline';
    analyzeBtn.disabled = true;
    uploadProgress.style.display = 'block';

    // Animate progress bar
    animateProgress();
  });
}

function animateProgress() {
  const stepDurations = [3000, 5000, 8000, 15000, 5000]; // ms per step
  let totalMs = stepDurations.reduce((a, b) => a + b, 0);
  let elapsed = 0;

  steps.forEach((step, i) => {
    let delay = stepDurations.slice(0, i).reduce((a, b) => a + b, 0);
    setTimeout(() => {
      steps.forEach(s => s.classList.remove('active'));
      step.classList.add('active');
      if (i > 0) steps[i - 1].classList.add('done');
      progressFill.style.width = ((delay + stepDurations[i]) / totalMs * 95) + '%';
    }, delay);
  });
}

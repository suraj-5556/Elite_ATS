/**
 * TalentAI - Main JavaScript
 * Global utilities used across all pages.
 */

"use strict";

// ── Auto-dismiss flash messages after 5s ───────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.flash').forEach(flash => {
    setTimeout(() => flash.remove(), 5000);
  });
});

// ── Toggle password visibility ─────────────────────────────────
function togglePassword(fieldId) {
  const input = document.getElementById(fieldId);
  if (!input) return;
  input.type = input.type === 'password' ? 'text' : 'password';
}

// ── Utility: Format file size ──────────────────────────────────
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

const container = document.getElementById('resultsContainer');
const noResults = document.getElementById('noResults');

const data = JSON.parse(sessionStorage.getItem('matchResults') || 'null');

if (!data) {
    noResults.style.display = 'block';
} else {
    noResults.style.display = 'none';
    renderResults(data);
}

function renderResults(d) {
    const final = d.final_result || {};
    const resume = d.resume || {};
    const job = d.job || {};
    const nlp = d.nlp_scores || {};
    const ml = d.ml_result || {};
    const claude = d.claude_eval || {};
    const skillOverlap = nlp.skill_overlap || {};
    const breakdown = final.score_breakdown || {};

    const score = final.final_score || 0;
    const circumference = 2 * Math.PI * 54;
    const offset = circumference - (score / 100) * circumference;
    const scoreColor = score >= 75 ? '#00ff88' : score >= 55 ? '#ffaa00' : '#ff4444';

    const html = `
    <div class="score-hero glass fade-in">
        <div class="score-ring-wrap">
            <svg class="score-ring" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="8"/>
                <circle cx="60" cy="60" r="54" fill="none" stroke="${scoreColor}" stroke-width="8"
                    stroke-dasharray="${circumference}" stroke-dashoffset="${offset}" stroke-linecap="round"
                    transform="rotate(-90 60 60)"
                    style="filter: drop-shadow(0 0 12px ${scoreColor}); transition: stroke-dashoffset 1.5s cubic-bezier(0.4,0,0.2,1)"/>
                <text x="60" y="52" text-anchor="middle" fill="white" font-size="24" font-weight="800" font-family="Inter">${score}%</text>
                <text x="60" y="68" text-anchor="middle" fill="rgba(255,255,255,0.55)" font-size="8" font-family="Inter">MATCH SCORE</text>
            </svg>
        </div>
        <div class="score-meta">
            <h2>${final.category || 'Analysis Complete'}</h2>
            <p>Shortlisting Probability: <strong style="color: ${scoreColor}">${final.shortlisting_probability || '—'}</strong></p>
            <div class="score-breakdown">
                <div class="score-part">
                    <span class="score-part-val">${breakdown.nlp_score || 0}%</span>
                    <span class="score-part-lbl">NLP Score</span>
                </div>
                <div class="score-part">
                    <span class="score-part-val">${breakdown.ml_score || 0}%</span>
                    <span class="score-part-lbl">ML Score</span>
                </div>
                <div class="score-part">
                    <span class="score-part-val">${breakdown.claude_score || 0}%</span>
                    <span class="score-part-lbl">Claude AI</span>
                </div>
                <div class="score-part">
                    <span class="score-part-val">${nlp.ats_score || 0}%</span>
                    <span class="score-part-lbl">ATS Score</span>
                </div>
            </div>
        </div>
    </div>

    <div class="results-grid">
        <!-- Matched Skills -->
        <div class="result-card glass fade-in">
            <h3>✅ Matched Required Skills (${(skillOverlap.matched_required || []).length})</h3>
            <div class="skill-chips">
                ${(skillOverlap.matched_required || []).map(s => `<span class="chip chip-matched">${s}</span>`).join('') || '<span style="color:var(--text-muted);font-size:0.85rem">No exact matches found</span>'}
            </div>
        </div>

        <!-- Missing Skills -->
        <div class="result-card glass fade-in">
            <h3>⚠️ Missing Critical Skills (${(skillOverlap.missing_required || []).length})</h3>
            <div class="skill-chips">
                ${(skillOverlap.missing_required || []).map(s => `<span class="chip chip-missing">${s}</span>`).join('') || '<span style="color:var(--green);font-size:0.85rem">All required skills matched!</span>'}
            </div>
            ${(skillOverlap.matched_preferred || []).length > 0 ? `
            <div style="margin-top:16px">
                <div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:8px;text-transform:uppercase;letter-spacing:1px">Preferred Skills Matched</div>
                <div class="skill-chips">
                    ${(skillOverlap.matched_preferred || []).map(s => `<span class="chip chip-preferred">${s}</span>`).join('')}
                </div>
            </div>` : ''}
        </div>

        <!-- ATS Score -->
        <div class="result-card glass fade-in">
            <h3>🤖 ATS Score</h3>
            <div class="ats-meter">
                <div class="ats-bar">
                    <div class="ats-fill" id="atsBar" style="width:0%"></div>
                </div>
                <div class="ats-labels">
                    <span>0%</span>
                    <span style="font-size:1rem;font-weight:700;color:${nlp.ats_score >= 70 ? 'var(--green)' : nlp.ats_score >= 50 ? 'var(--orange)' : 'var(--red)'}">${nlp.ats_score || 0}%</span>
                    <span>100%</span>
                </div>
            </div>
            <div style="margin-top:16px;display:grid;grid-template-columns:1fr 1fr;gap:12px">
                <div class="score-part">
                    <span class="score-part-val">${((nlp.tfidf_similarity || 0)*100).toFixed(0)}%</span>
                    <span class="score-part-lbl">TF-IDF Similarity</span>
                </div>
                <div class="score-part">
                    <span class="score-part-val">${((nlp.experience_match || 0)*100).toFixed(0)}%</span>
                    <span class="score-part-lbl">Experience Match</span>
                </div>
            </div>
        </div>

        <!-- Resume Info -->
        <div class="result-card glass fade-in">
            <h3>📋 Resume Summary</h3>
            <div style="display:flex;flex-direction:column;gap:10px;font-size:0.88rem">
                <div style="display:flex;justify-content:space-between;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:8px;border:1px solid rgba(255,255,255,0.07)">
                    <span style="color:var(--text-secondary)">Experience</span>
                    <span style="font-weight:600">${resume.experience_years || 0} years</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:8px;border:1px solid rgba(255,255,255,0.07)">
                    <span style="color:var(--text-secondary)">Skills Found</span>
                    <span style="font-weight:600">${(resume.skills || []).length}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:8px;border:1px solid rgba(255,255,255,0.07)">
                    <span style="color:var(--text-secondary)">Certifications</span>
                    <span style="font-weight:600">${(resume.certifications || []).length}</span>
                </div>
                <div style="display:flex;justify-content:space-between;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:8px;border:1px solid rgba(255,255,255,0.07)">
                    <span style="color:var(--text-secondary)">Job Requires</span>
                    <span style="font-weight:600">${job.experience_required || 0}+ years</span>
                </div>
            </div>
        </div>

        <!-- Claude Assessment -->
        <div class="result-card glass fade-in" style="grid-column: span 2">
            <h3>✨ AI Assessment ${claude.source === 'mock' ? '<span style="font-size:0.7rem;opacity:0.5">(Demo mode)</span>' : '<span style="font-size:0.7rem;color:var(--cyan)">(Claude AI)</span>'}</h3>
            <div class="assessment-text">${claude.overall_assessment || 'Analysis complete.'}</div>
            <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">
                <span class="recommended-action ${getActionClass(claude.recommended_action)}">
                    ${getActionEmoji(claude.recommended_action)} ${claude.recommended_action || 'Review Required'}
                </span>
                <span style="font-size:0.85rem;color:var(--text-muted)">Interview Likelihood: <strong style="color:var(--text-primary)">${claude.interview_likelihood || '—'}</strong></span>
            </div>
        </div>

        <!-- Improvement Suggestions -->
        <div class="result-card glass fade-in" style="grid-column: span 2">
            <h3>💡 Improvement Suggestions</h3>
            <div class="suggestion-list">
                ${(claude.improvement_suggestions || ['Add measurable achievements', 'Include relevant projects', 'Tailor resume to job description']).map((s, i) => `
                    <div class="suggestion-item">
                        <span class="suggestion-icon">${['🎯','📈','🔧','⚡','🌟'][i % 5]}</span>
                        <span>${s}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    </div>

    <div style="text-align:center;margin-top:32px;display:flex;gap:16px;justify-content:center">
        <a href="/match/" class="btn btn-primary btn-lg">🔄 Analyze Another Resume</a>
        <a href="/jobs/" class="btn btn-ghost btn-lg">Browse Jobs →</a>
    </div>
    `;

    container.innerHTML = html;

    // Animate ATS bar
    setTimeout(() => {
        const atsBar = document.getElementById('atsBar');
        if (atsBar) atsBar.style.width = (nlp.ats_score || 0) + '%';
    }, 300);
}

function getActionClass(action) {
    if (!action) return 'action-improve';
    if (action.includes('Confidently')) return 'action-confident';
    if (action.includes('Gaps') || action.includes('Not')) return 'action-gaps';
    return 'action-improve';
}

function getActionEmoji(action) {
    if (!action) return '📋';
    if (action.includes('Confidently')) return '🚀';
    if (action.includes('Improvements')) return '⚠️';
    if (action.includes('Gaps')) return '🔴';
    if (action.includes('Not')) return '❌';
    return '📋';
}

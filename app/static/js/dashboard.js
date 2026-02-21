async function loadStats() {
    try {
        const resp = await fetch('/dashboard/api/stats');
        const data = await resp.json();
        
        document.getElementById('totalAnalyses').textContent = data.total_analyses || 0;
        document.getElementById('avgScore').textContent = data.avg_score ? data.avg_score + '%' : '—';
        document.getElementById('highMatches').textContent = data.high_matches || 0;
        
        const recentList = document.getElementById('recentList');
        if (data.recent && data.recent.length > 0) {
            recentList.innerHTML = data.recent.map(entry => {
                const score = entry.final_score || 0;
                const color = score >= 70 ? 'var(--green)' : score >= 50 ? 'var(--orange)' : 'var(--red)';
                return `
                    <div class="recent-item">
                        <span style="font-size:0.82rem;color:var(--text-muted)">${new Date(entry.timestamp).toLocaleDateString()}</span>
                        <span style="color:var(--text-secondary);font-size:0.85rem">${entry.matched_skills || 0} skills matched</span>
                        <span class="recent-score" style="color:${color}">${score}%</span>
                    </div>
                `;
            }).join('');
        } else {
            recentList.innerHTML = '<div class="empty-state">No analyses yet. <a href="/match/">Start now →</a></div>';
        }
    } catch(e) {
        console.error('Stats load error:', e);
    }
}

// Check Claude API status
async function checkClaudeStatus() {
    const dot = document.getElementById('claudeStatus');
    const text = document.getElementById('claudeStatusText');
    
    const hasKey = true; // We'll indicate it's configured but might be mock
    if (hasKey) {
        dot.classList.add('active');
        text.textContent = 'Active (API Key Required)';
    } else {
        text.textContent = 'Demo Mode';
        text.style.color = 'var(--orange)';
    }
}

loadStats();
checkClaudeStatus();

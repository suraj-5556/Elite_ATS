let jobsData = [];

async function loadJobs() {
    try {
        const resp = await fetch('/jobs/api/list');
        const data = await resp.json();
        jobsData = data.jobs;
    } catch(e) {
        // Use data from rendered template
    }
}

loadJobs();

// Search filter
document.getElementById('jobSearch').addEventListener('input', function() {
    const q = this.value.toLowerCase();
    document.querySelectorAll('.job-card').forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(q) ? 'flex' : 'none';
    });
});

async function viewJob(id) {
    try {
        const resp = await fetch(`/jobs/api/${id}`);
        const job = await resp.json();
        
        document.getElementById('modalBody').innerHTML = `
            <div style="margin-bottom:24px">
                <h2 style="font-size:1.5rem;font-weight:800;margin-bottom:8px">${job.title}</h2>
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px">
                    <div class="company-avatar">${job.company[0]}</div>
                    <div>
                        <p style="font-weight:600">${job.company}</p>
                        <p style="color:var(--text-muted);font-size:0.85rem">📍 ${job.location} · ${job.type}</p>
                    </div>
                </div>
                <div style="display:flex;gap:6px;flex-wrap:wrap">
                    ${job.tags.map(t => `<span class="tag">${t}</span>`).join('')}
                </div>
            </div>
            <pre style="white-space:pre-wrap;font-family:inherit;font-size:0.9rem;color:var(--text-secondary);line-height:1.7">${job.description}</pre>
        `;
        
        document.getElementById('modalApplyBtn').onclick = () => applyToJob(id);
        document.getElementById('jobModal').style.display = 'flex';
    } catch(e) {
        console.error(e);
    }
}

async function applyToJob(id) {
    try {
        const resp = await fetch(`/jobs/api/${id}`);
        const job = await resp.json();
        sessionStorage.setItem('prefillJD', job.description);
        window.location.href = '/match/';
    } catch(e) {
        window.location.href = '/match/';
    }
}

function closeModal() {
    document.getElementById('jobModal').style.display = 'none';
}

document.getElementById('jobModal').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
});

// Prefill JD if coming from jobs page
const prefillJD = sessionStorage.getItem('prefillJD');
if (prefillJD) {
    sessionStorage.removeItem('prefillJD');
}

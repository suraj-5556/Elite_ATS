const SAMPLE_JDS = {
    1: `Senior Data Scientist

We are looking for a Senior Data Scientist with 5+ years of experience.

Required Skills:
- Python (pandas, numpy, scikit-learn)
- Machine learning and deep learning (TensorFlow, PyTorch)
- SQL and database management
- NLP and natural language processing
- Statistical analysis and hypothesis testing
- MLflow for experiment tracking
- Docker and containerization

Preferred Skills:
- AWS or GCP cloud platforms
- Kubernetes and CI/CD pipelines
- Spark and big data processing

Responsibilities:
- Build and deploy production ML models
- Lead end-to-end data science projects
- Collaborate with engineering teams
- Mentor junior data scientists
- Conduct statistical analysis and A/B testing

Requirements:
- 5+ years of experience in data science
- Master's or PhD in Computer Science, Statistics, or related field
- Strong communication and leadership skills`,

    2: `Machine Learning Engineer

Required Skills:
- Python, Golang or Java
- ML frameworks: scikit-learn, XGBoost, LightGBM
- MLOps: MLflow, Airflow, DVC, Kubeflow
- Docker, Kubernetes, CI/CD pipelines
- AWS or GCP cloud platforms
- REST API development with Flask or FastAPI
- SQL and NoSQL databases

Responsibilities:
- Design and implement scalable ML pipelines
- Deploy and monitor ML models in production
- Build data infrastructure and ETL pipelines
- Optimize model performance and latency
- Collaborate with data scientists

Requirements:
- 3+ years of ML engineering experience
- Strong software engineering fundamentals
- Experience with distributed systems`,

    3: `NLP Research Engineer

Required Skills:
- Python for deep learning
- NLP libraries: NLTK, spaCy, Transformers
- HuggingFace ecosystem and LLMs
- BERT, GPT, T5 model architectures
- Fine-tuning and transfer learning
- Machine learning (classification, NER, summarization)

Preferred:
- Experience with LLM APIs (OpenAI, Anthropic, etc.)
- Reinforcement learning from human feedback (RLHF)
- Research background or publications

Responsibilities:
- Research and implement state-of-the-art NLP models
- Fine-tune LLMs for downstream tasks
- Build text processing pipelines
- Write technical documentation and research reports

Requirements:
- 3-5 years of NLP/ML experience
- Master's or PhD preferred
- Published research or open source contributions`
};

// File Upload
const uploadZone = document.getElementById('uploadZone');
const resumeFile = document.getElementById('resumeFile');
const uploadContent = document.getElementById('uploadContent');
const uploadSuccess = document.getElementById('uploadSuccess');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFile = document.getElementById('removeFile');

uploadZone.addEventListener('click', () => resumeFile.click());

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
});

uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    if (e.dataTransfer.files[0]) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
});

resumeFile.addEventListener('change', () => {
    if (resumeFile.files[0]) handleFileSelect(resumeFile.files[0]);
});

function handleFileSelect(file) {
    const allowed = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const allowedExt = ['pdf', 'docx', 'txt'];
    const ext = file.name.split('.').pop().toLowerCase();
    
    if (!allowedExt.includes(ext)) {
        showToast('❌ Invalid file type. Please use PDF, DOCX, or TXT', 'error');
        return;
    }
    
    if (file.size > 16 * 1024 * 1024) {
        showToast('❌ File too large (max 16MB)', 'error');
        return;
    }
    
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    uploadContent.style.display = 'none';
    uploadSuccess.style.display = 'block';
}

removeFile.addEventListener('click', (e) => {
    e.stopPropagation();
    resumeFile.value = '';
    uploadContent.style.display = 'block';
    uploadSuccess.style.display = 'none';
});

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// JD Counter
const jdText = document.getElementById('jdText');
const jdCount = document.getElementById('jdCount');
jdText.addEventListener('input', () => jdCount.textContent = jdText.value.length);

function loadSampleJD(num) {
    jdText.value = SAMPLE_JDS[num];
    jdCount.textContent = jdText.value.length;
}

// Form Submit
const matchForm = document.getElementById('matchForm');
const analyzeBtn = document.getElementById('analyzeBtn');
const btnText = document.getElementById('btnText');
const btnLoader = document.getElementById('btnLoader');
const loadingOverlay = document.getElementById('loadingOverlay');

const loadingSteps = ['step1', 'step2', 'step3', 'step4', 'step5'];
let stepIndex = 0;
let stepInterval;

function startLoadingAnimation() {
    stepIndex = 0;
    loadingSteps.forEach(id => {
        const el = document.getElementById(id);
        el.classList.remove('active', 'done');
    });
    
    document.getElementById(loadingSteps[0]).classList.add('active');
    stepIndex = 1;
    
    stepInterval = setInterval(() => {
        if (stepIndex < loadingSteps.length) {
            document.getElementById(loadingSteps[stepIndex - 1]).classList.remove('active');
            document.getElementById(loadingSteps[stepIndex - 1]).classList.add('done');
            document.getElementById(loadingSteps[stepIndex]).classList.add('active');
            stepIndex++;
        }
    }, 2500);
}

function stopLoadingAnimation() {
    clearInterval(stepInterval);
    loadingSteps.forEach(id => {
        document.getElementById(id).classList.add('done');
        document.getElementById(id).classList.remove('active');
    });
}

matchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!resumeFile.files[0]) {
        showToast('❌ Please upload your resume first', 'error');
        return;
    }
    
    if (!jdText.value.trim() || jdText.value.trim().length < 50) {
        showToast('❌ Please paste a job description (min 50 characters)', 'error');
        return;
    }
    
    // Show loading
    analyzeBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'flex';
    loadingOverlay.style.display = 'flex';
    startLoadingAnimation();
    
    const formData = new FormData();
    formData.append('resume', resumeFile.files[0]);
    formData.append('jd_text', jdText.value.trim());
    
    try {
        const response = await fetch('/match/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok || data.error) {
            throw new Error(data.error || 'Analysis failed');
        }
        
        stopLoadingAnimation();
        await new Promise(r => setTimeout(r, 500));
        
        // Store results and navigate
        sessionStorage.setItem('matchResults', JSON.stringify(data));
        window.location.href = '/match/results';
        
    } catch (err) {
        stopLoadingAnimation();
        loadingOverlay.style.display = 'none';
        analyzeBtn.disabled = false;
        btnText.style.display = 'flex';
        btnLoader.style.display = 'none';
        showToast('❌ ' + err.message, 'error');
    }
});

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed; bottom: 24px; right: 24px; z-index: 1000;
        padding: 14px 20px; border-radius: 12px; font-size: 0.9rem;
        background: ${type === 'error' ? 'rgba(255,68,68,0.15)' : 'rgba(0,255,136,0.15)'};
        border: 1px solid ${type === 'error' ? 'rgba(255,68,68,0.4)' : 'rgba(0,255,136,0.4)'};
        color: ${type === 'error' ? '#ff4444' : '#00ff88'};
        backdrop-filter: blur(20px);
        animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

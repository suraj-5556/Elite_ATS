from flask import Blueprint, request, jsonify, render_template

jobs_bp = Blueprint('jobs', __name__)

SAMPLE_JOBS = [
    {
        'id': 1,
        'title': 'Senior Data Scientist',
        'company': 'TechCorp AI',
        'location': 'Remote',
        'type': 'Full-time',
        'description': '''We are looking for a Senior Data Scientist to join our ML team.

Required Skills:
- Python, R for data analysis
- Machine learning and deep learning frameworks (TensorFlow, PyTorch, scikit-learn)
- SQL and data pipeline experience
- NLP and computer vision experience preferred
- MLflow, DVC for ML operations
- Docker and Kubernetes for deployment

Responsibilities:
- Build and deploy ML models at scale
- Lead data science projects end-to-end
- Collaborate with engineering teams for model deployment
- Mentor junior data scientists
- Conduct A/B tests and statistical analysis

Requirements:
- 5+ years of experience in data science or ML engineering
- Strong statistics and mathematics background
- Experience with cloud platforms (AWS, GCP, Azure)
- Bachelor's or Master's degree in Computer Science, Statistics, or related field''',
        'tags': ['Python', 'ML', 'Deep Learning', 'Docker']
    },
    {
        'id': 2,
        'title': 'Machine Learning Engineer',
        'company': 'DataDriven Inc.',
        'location': 'Hybrid - Mumbai',
        'type': 'Full-time',
        'description': '''We need a Machine Learning Engineer to productionize our ML systems.

Required Skills:
- Python, Golang
- ML frameworks: scikit-learn, XGBoost, LightGBM
- MLOps tools: MLflow, Airflow, DVC
- Docker, Kubernetes, CI/CD
- AWS or GCP cloud platforms
- REST API development with Flask or FastAPI
- SQL and NoSQL databases

Responsibilities:
- Design and implement ML pipelines
- Deploy models to production at scale
- Monitor model performance and drift
- Build data infrastructure and ETL pipelines
- Collaborate with data scientists and software engineers

Requirements:
- 3+ years of ML engineering experience
- Strong software engineering fundamentals
- Experience with large-scale distributed systems''',
        'tags': ['MLOps', 'Docker', 'Python', 'AWS']
    },
    {
        'id': 3,
        'title': 'Junior Data Analyst',
        'company': 'InsightCo',
        'location': 'Bangalore',
        'type': 'Full-time',
        'description': '''Entry-level Data Analyst position for fresh graduates.

Required Skills:
- Python or R for data analysis
- SQL for database queries
- Excel and data visualization tools
- Basic statistics knowledge
- Tableau or Power BI preferred

Responsibilities:
- Analyze datasets to extract business insights
- Create dashboards and reports
- Support senior analysts in data projects
- Maintain data quality and integrity

Requirements:
- 0-2 years of experience
- Bachelor's degree in any quantitative field
- Strong analytical and communication skills''',
        'tags': ['SQL', 'Python', 'Tableau', 'Analytics']
    },
    {
        'id': 4,
        'title': 'NLP Engineer',
        'company': 'LanguageTech',
        'location': 'Remote',
        'type': 'Full-time',
        'description': '''Build the next generation of NLP systems.

Required Skills:
- Python, deep learning frameworks
- NLP libraries: NLTK, spaCy, Transformers (HuggingFace)
- BERT, GPT, and other LLM architectures
- Machine learning and fine-tuning techniques
- Experience with text classification, NER, summarization

Responsibilities:
- Research and implement NLP models
- Fine-tune LLMs for specific tasks
- Build text processing pipelines
- Optimize model inference performance
- Write technical documentation

Requirements:
- 3-5 years of NLP experience
- Published research or open source contributions preferred
- Master's or PhD in CS, Linguistics, or related field''',
        'tags': ['NLP', 'LLM', 'Python', 'Transformers']
    },
]

@jobs_bp.route('/')
def list_jobs():
    return render_template('jobs.html', jobs=SAMPLE_JOBS)

@jobs_bp.route('/api/list')
def api_list_jobs():
    return jsonify({'jobs': SAMPLE_JOBS})

@jobs_bp.route('/api/<int:job_id>')
def api_get_job(job_id):
    job = next((j for j in SAMPLE_JOBS if j['id'] == job_id), None)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)

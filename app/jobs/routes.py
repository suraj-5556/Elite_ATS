"""
Jobs routes: Browse open positions.
Sample jobs are hardcoded for demo; in production, connect to a jobs collection.
"""

from flask import render_template
from flask_login import login_required
from app.jobs import jobs_bp

SAMPLE_JOBS = [
    {
        'id': 'j001',
        'title': 'Senior Python Engineer',
        'company': 'TechCorp Inc.',
        'location': 'San Francisco, CA (Hybrid)',
        'type': 'Full-time',
        'salary': '$140,000 – $180,000',
        'tags': ['Python', 'Flask', 'MongoDB', 'AWS', 'REST APIs'],
        'description': (
            'We are looking for a Senior Python Engineer to join our platform team. '
            'You will design scalable microservices, mentor junior engineers, and drive '
            'technical decisions. Experience with cloud deployments and Docker required.'
        ),
        'jd': (
            'Senior Python Engineer with 5+ years experience in Python, Flask/Django, '
            'REST API design, MongoDB, PostgreSQL, Docker, Kubernetes, AWS/GCP, '
            'CI/CD pipelines, unit testing, and agile development.'
        ),
    },
    {
        'id': 'j002',
        'title': 'Machine Learning Engineer',
        'company': 'AI Innovations Ltd.',
        'location': 'Remote',
        'type': 'Full-time',
        'salary': '$130,000 – $170,000',
        'tags': ['Python', 'PyTorch', 'scikit-learn', 'MLflow', 'NLP'],
        'description': (
            'Join our ML team to build production-grade models for NLP and recommendation '
            'systems. You\'ll own the full ML lifecycle from research to deployment.'
        ),
        'jd': (
            'Machine Learning Engineer with expertise in Python, PyTorch, TensorFlow, '
            'scikit-learn, NLP, BERT, transformers, MLflow, model deployment, A/B testing, '
            'feature engineering, statistical analysis, and data pipelines.'
        ),
    },
    {
        'id': 'j003',
        'title': 'Full Stack Developer',
        'company': 'StartupXYZ',
        'location': 'New York, NY',
        'type': 'Full-time',
        'salary': '$100,000 – $130,000',
        'tags': ['React', 'Node.js', 'TypeScript', 'PostgreSQL', 'Docker'],
        'description': (
            'Fast-growing startup seeking a versatile full stack developer to build '
            'customer-facing products. You\'ll work across the entire stack in a fast-paced environment.'
        ),
        'jd': (
            'Full Stack Developer proficient in React, Node.js, TypeScript, JavaScript, '
            'PostgreSQL, MongoDB, REST APIs, GraphQL, Docker, Git, agile methodology, '
            'responsive design, and system architecture.'
        ),
    },
    {
        'id': 'j004',
        'title': 'Data Scientist',
        'company': 'Analytics Pro',
        'location': 'Chicago, IL (On-site)',
        'type': 'Full-time',
        'salary': '$115,000 – $145,000',
        'tags': ['Python', 'R', 'SQL', 'Tableau', 'Statistics'],
        'description': (
            'Analytics Pro is seeking a Data Scientist to derive insights from complex datasets, '
            'build predictive models, and present findings to C-suite stakeholders.'
        ),
        'jd': (
            'Data Scientist with strong skills in Python, R, SQL, statistical modeling, '
            'machine learning, data visualization, Tableau, PowerBI, Pandas, NumPy, '
            'hypothesis testing, A/B testing, and business intelligence.'
        ),
    },
    {
        'id': 'j005',
        'title': 'DevOps Engineer',
        'company': 'CloudFirst',
        'location': 'Austin, TX (Hybrid)',
        'type': 'Full-time',
        'salary': '$120,000 – $155,000',
        'tags': ['Kubernetes', 'Terraform', 'AWS', 'CI/CD', 'Linux'],
        'description': (
            'Build and maintain scalable infrastructure for millions of users. '
            'You\'ll own CI/CD pipelines, container orchestration, and cloud cost optimization.'
        ),
        'jd': (
            'DevOps Engineer experienced with AWS, GCP, Kubernetes, Docker, Terraform, '
            'Ansible, Jenkins, GitHub Actions, Linux, bash scripting, monitoring, '
            'logging, Grafana, Prometheus, and incident response.'
        ),
    },
    {
        'id': 'j006',
        'title': 'Frontend Engineer',
        'company': 'DesignLab',
        'location': 'Remote',
        'type': 'Contract',
        'salary': '$80 – $110/hour',
        'tags': ['React', 'Vue.js', 'CSS', 'Figma', 'TypeScript'],
        'description': (
            'Pixel-perfect frontend engineer needed to implement complex UI designs. '
            'Strong CSS skills and design sensibility required.'
        ),
        'jd': (
            'Frontend Engineer skilled in React, Vue.js, TypeScript, JavaScript, '
            'HTML5, CSS3, SASS, Figma, responsive design, accessibility, '
            'performance optimization, webpack, and cross-browser compatibility.'
        ),
    },
]


@jobs_bp.route('/jobs')
@login_required
def index():
    return render_template('jobs/index.html', jobs=SAMPLE_JOBS)

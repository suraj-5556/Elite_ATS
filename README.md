# ⚡ TalentAI — AI Job Portal with Resume Matching

> Full-stack AI-powered job portal built with Python, Flask, Traditional NLP, ML, and Claude AI

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Build the image
docker build -t ai-job-portal .

# Run with your Claude API key
docker run -p 5000:5000 \
  -e ANTHROPIC_API_KEY=your-key-here \
  ai-job-portal

# Open http://localhost:5000
```

### Option 2: Local Development

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download NLP models
python -m nltk.downloader punkt stopwords punkt_tab

# 4. Set your API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 5. Run
python app.py

# Open http://localhost:5000
```

---

## 🏗️ Project Structure

```
job_portal_ml/
│
├── app/
│   ├── routes/
│   │   ├── main.py          # Landing & analyze pages
│   │   ├── resume.py        # Resume upload API
│   │   ├── jobs.py          # Job listings API
│   │   ├── match.py         # Matching analysis API
│   │   └── dashboard.py     # Dashboard & stats
│   │
│   ├── templates/
│   │   ├── base.html        # Base layout with navbar
│   │   ├── index.html       # Landing page
│   │   ├── match.html       # Resume upload + JD input
│   │   ├── results.html     # Analysis results
│   │   ├── jobs.html        # Job listings
│   │   └── dashboard.html   # User dashboard
│   │
│   ├── static/
│   │   ├── css/main.css     # Dark glassmorphism UI
│   │   └── js/              # Page-specific JS files
│   │
│   └── services/
│       ├── resume_parser.py  # PDF/DOCX/TXT parsing
│       ├── jd_parser.py      # Job description NLP
│       ├── nlp_scorer.py     # TF-IDF + cosine similarity
│       ├── ml_model.py       # Gradient Boosting model
│       ├── claude_evaluator.py # Claude AI integration
│       └── matcher.py        # Orchestration pipeline
│
├── ml_models/
│   ├── training/train.py    # MLflow training pipeline
│   ├── inference/           # Saved models
│   └── datasets/            # Training data (DVC)
│
├── uploads/                 # Temporary resume storage
├── experiments/             # MLflow runs
├── logs/                    # App & prediction logs
│
├── app.py                   # Flask entry point
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── .env.example
```

---

## 🧠 AI Pipeline

```
Resume (PDF/DOCX/TXT)
        ↓
  [Resume Parser]
  spaCy + PyMuPDF + python-docx
  → Skills, Experience, Education, Certifications
        ↓
  [JD Parser]
  NLTK + Regex
  → Required Skills, Keywords, Experience Requirements
        ↓
  [NLP Scorer]                    Weight: 35%
  TF-IDF + Cosine Similarity
  Keyword Density + Experience Match
        ↓
  [ML Model]                      Weight: 30%
  Gradient Boosting Classifier
  (Trained on 2000 synthetic samples)
        ↓
  [Claude AI Evaluator]           Weight: 35%
  claude-sonnet-4-20250514
  Shortlisting probability + Suggestions
        ↓
  FINAL MATCH SCORE (0-100%)
```

---

## 📊 Output

- **Match Score**: Composite 0-100% from NLP + ML + Claude AI
- **ATS Score**: Keyword density for Applicant Tracking Systems
- **Shortlisting Probability**: High / Medium / Low
- **Matched Skills**: Skills present in both resume and JD
- **Missing Skills**: Required skills not in resume
- **Improvement Suggestions**: Actionable recommendations
- **Interview Likelihood**: AI-estimated probability

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask 3.0 |
| Resume Parsing | PyMuPDF, python-docx, NLTK |
| NLP | TF-IDF, Cosine Similarity, spaCy |
| ML Model | Scikit-learn, Gradient Boosting |
| AI Evaluation | Anthropic Claude (claude-sonnet-4) |
| MLOps | MLflow |
| Frontend | HTML5, CSS3 (Glassmorphism), Vanilla JS |
| Deployment | Docker |

---

## 🤖 MLflow Training

```bash
# Run the training pipeline manually
python ml_models/training/train.py

# View MLflow dashboard
mlflow ui --backend-store-uri experiments/mlruns
# Open http://localhost:5000
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Claude AI API key |
| `SECRET_KEY` | No | Flask secret (auto-generated) |
| `FLASK_DEBUG` | No | Enable debug mode |

**Without an API key**, the portal still works using a rule-based fallback evaluator.

---

## 📁 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Landing page |
| GET | `/jobs/` | Job listings |
| GET | `/match/` | Analysis form |
| POST | `/match/analyze` | Run resume analysis |
| GET | `/match/results` | Results page |
| GET | `/dashboard/` | User dashboard |
| GET | `/dashboard/api/stats` | Stats JSON |
| GET | `/jobs/api/list` | Jobs JSON |

---

## 🐳 Docker Commands

```bash
# Build
docker build -t ai-job-portal .

# Run with API key
docker run -p 5000:5000 -e ANTHROPIC_API_KEY=sk-ant-xxx ai-job-portal

# Run with .env file
docker run -p 5000:5000 --env-file .env ai-job-portal

# Run detached
docker run -d -p 5000:5000 --env-file .env --name talentai ai-job-portal

# View logs
docker logs talentai -f

# Stop
docker stop talentai
```

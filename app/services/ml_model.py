import os
import logging
import numpy as np
import joblib
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from typing import Dict, Tuple
import json

logger = logging.getLogger(__name__)

MODEL_PATH = 'ml_models/inference/resume_matcher.pkl'
SCALER_PATH = 'ml_models/inference/scaler.pkl'

def generate_synthetic_training_data(n_samples: int = 500) -> Tuple[np.ndarray, np.ndarray]:
    """Generate synthetic training data based on feature distributions"""
    np.random.seed(42)
    
    X = []
    y = []
    
    for _ in range(n_samples):
        # Features: skill_overlap, tfidf_sim, keyword_density, exp_match, ats_score_norm
        if np.random.random() < 0.4:  # Positive match
            skill_overlap = np.random.uniform(0.55, 1.0)
            tfidf = np.random.uniform(0.4, 0.9)
            keyword = np.random.uniform(0.4, 0.9)
            exp_match = np.random.uniform(0.7, 1.0)
            ats = np.random.uniform(0.6, 1.0)
            label = 1
        else:  # Poor match
            skill_overlap = np.random.uniform(0.0, 0.45)
            tfidf = np.random.uniform(0.0, 0.35)
            keyword = np.random.uniform(0.0, 0.35)
            exp_match = np.random.uniform(0.0, 0.65)
            ats = np.random.uniform(0.1, 0.55)
            label = 0
        
        # Add some noise
        noise = np.random.normal(0, 0.05, 5)
        features = np.clip([skill_overlap, tfidf, keyword, exp_match, ats] + noise, 0, 1)
        X.append(features)
        y.append(label)
    
    return np.array(X), np.array(y)

def train_model() -> Pipeline:
    logger.info("Training ML model...")
    os.makedirs('ml_models/inference', exist_ok=True)
    os.makedirs('ml_models/training', exist_ok=True)
    
    X, y = generate_synthetic_training_data(1000)
    
    # Gradient Boosting as primary model
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', GradientBoostingClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            random_state=42
        ))
    ])
    
    # Cross-validation
    cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring='accuracy')
    logger.info(f"CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")
    
    pipeline.fit(X, y)
    
    joblib.dump(pipeline, MODEL_PATH)
    
    # Save metadata
    metadata = {
        'cv_accuracy': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std()),
        'features': ['skill_overlap', 'tfidf_similarity', 'keyword_density', 'experience_match', 'ats_score_norm'],
        'model_type': 'GradientBoosting',
        'training_samples': 1000
    }
    with open('ml_models/inference/model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Model saved to {MODEL_PATH}")
    return pipeline

def load_or_train_model() -> Pipeline:
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            logger.info("Loaded existing ML model")
            return model
        except Exception as e:
            logger.warning(f"Failed to load model: {e}. Retraining...")
    
    return train_model()

def extract_ml_features(nlp_scores: Dict) -> np.ndarray:
    skill_overlap = nlp_scores.get('skill_overlap', {}).get('skill_overlap_score', 0)
    tfidf = nlp_scores.get('tfidf_similarity', 0)
    keyword_density = nlp_scores.get('keyword_density', 0)
    exp_match = nlp_scores.get('experience_match', 0)
    ats_norm = nlp_scores.get('ats_score', 0) / 100.0
    
    return np.array([[skill_overlap, tfidf, keyword_density, exp_match, ats_norm]])

def predict_match_score(nlp_scores: Dict) -> Dict:
    model = load_or_train_model()
    features = extract_ml_features(nlp_scores)
    
    try:
        prob = model.predict_proba(features)[0]
        match_probability = float(prob[1])  # Probability of positive match
        prediction = int(model.predict(features)[0])
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        # Fallback: use NLP composite score
        match_probability = nlp_scores.get('nlp_composite_score', 0.5)
        prediction = 1 if match_probability > 0.5 else 0
    
    # ML score as percentage
    ml_score = match_probability * 100
    
    return {
        'ml_match_probability': round(match_probability, 3),
        'ml_score': round(ml_score, 1),
        'ml_prediction': 'Match' if prediction == 1 else 'No Match',
        'features_used': ['skill_overlap', 'tfidf_similarity', 'keyword_density', 'experience_match', 'ats_score'],
    }

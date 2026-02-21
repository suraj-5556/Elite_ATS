#!/usr/bin/env python3
"""
ML Training Pipeline for Resume-Job Matching
Includes MLflow experiment tracking and model evaluation
"""

import os
import sys
import json
import logging
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                               f1_score, roc_auc_score, classification_report)
import joblib

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Directories
os.makedirs('ml_models/training', exist_ok=True)
os.makedirs('ml_models/inference', exist_ok=True)
os.makedirs('ml_models/datasets', exist_ok=True)
os.makedirs('experiments', exist_ok=True)

FEATURE_NAMES = ['skill_overlap', 'tfidf_similarity', 'keyword_density', 'experience_match', 'ats_score_norm']

def generate_training_data(n_samples: int = 2000) -> tuple:
    """Generate synthetic labeled dataset for training"""
    np.random.seed(42)
    X, y = [], []
    
    for _ in range(n_samples):
        # Positive examples (35% of data)
        if np.random.random() < 0.35:
            skill_overlap = np.random.beta(5, 2)  # Skewed high
            tfidf = np.random.beta(4, 2)
            keyword = np.random.beta(4, 2)
            exp_match = np.random.beta(5, 1.5)
            ats = np.random.beta(4, 2)
            label = 1
        # Borderline cases (15%)
        elif np.random.random() < 0.15:
            skill_overlap = np.random.uniform(0.40, 0.60)
            tfidf = np.random.uniform(0.30, 0.55)
            keyword = np.random.uniform(0.30, 0.55)
            exp_match = np.random.uniform(0.50, 0.80)
            ats = np.random.uniform(0.40, 0.65)
            label = np.random.choice([0, 1])
        # Negative examples (50%)
        else:
            skill_overlap = np.random.beta(2, 5)  # Skewed low
            tfidf = np.random.beta(2, 4)
            keyword = np.random.beta(2, 4)
            exp_match = np.random.beta(2, 4)
            ats = np.random.beta(2, 4)
            label = 0
        
        noise = np.random.normal(0, 0.03, 5)
        features = np.clip([skill_overlap, tfidf, keyword, exp_match, ats] + noise, 0, 1)
        X.append(features)
        y.append(label)
    
    return np.array(X), np.array(y)

def save_dataset(X: np.ndarray, y: np.ndarray):
    """Save dataset for DVC versioning"""
    dataset = {
        'features': X.tolist(),
        'labels': y.tolist(),
        'feature_names': FEATURE_NAMES,
        'n_samples': len(y),
        'positive_rate': float(y.mean())
    }
    with open('ml_models/datasets/training_data.json', 'w') as f:
        json.dump(dataset, f)
    logger.info(f"Dataset saved: {len(y)} samples, {y.mean():.1%} positive rate")

def train_and_evaluate(model_name: str, model, X_train, X_test, y_train, y_test):
    """Train a model and log metrics with MLflow"""
    
    with mlflow.start_run(run_name=model_name, nested=True):
        # Train
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_prob),
        }
        
        # CV score
        cv_scores = cross_val_score(model, np.vstack([X_train, X_test]), 
                                     np.hstack([y_train, y_test]), cv=5)
        metrics['cv_mean'] = cv_scores.mean()
        metrics['cv_std'] = cv_scores.std()
        
        # Log to MLflow
        mlflow.log_metrics(metrics)
        mlflow.log_params({
            'model_type': model_name,
            'n_train': len(X_train),
            'n_test': len(X_test),
        })
        
        logger.info(f"\n{'='*40}")
        logger.info(f"Model: {model_name}")
        logger.info(f"Accuracy: {metrics['accuracy']:.3f}")
        logger.info(f"F1 Score: {metrics['f1']:.3f}")
        logger.info(f"ROC AUC: {metrics['roc_auc']:.3f}")
        logger.info(f"CV: {metrics['cv_mean']:.3f} (+/- {metrics['cv_std']:.3f})")
        
        return metrics, model

def run_training_pipeline():
    logger.info("="*50)
    logger.info("Starting ML Training Pipeline")
    logger.info("="*50)
    
    # Setup MLflow
    mlflow.set_tracking_uri('experiments/mlruns')
    mlflow.set_experiment('resume_matcher')
    
    # Generate data
    X, y = generate_training_data(n_samples=2000)
    save_dataset(X, y)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")
    
    # Define models
    models = {
        'LogisticRegression': Pipeline([
            ('scaler', StandardScaler()),
            ('model', LogisticRegression(C=1.0, random_state=42, max_iter=1000))
        ]),
        'RandomForest': Pipeline([
            ('scaler', StandardScaler()),
            ('model', RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42))
        ]),
        'GradientBoosting': Pipeline([
            ('scaler', StandardScaler()),
            ('model', GradientBoostingClassifier(n_estimators=100, max_depth=4, 
                                                  learning_rate=0.1, random_state=42))
        ]),
    }
    
    best_model = None
    best_f1 = 0
    best_name = ''
    results = {}
    
    with mlflow.start_run(run_name='resume_matcher_comparison'):
        mlflow.log_param('n_samples', len(X))
        mlflow.log_param('n_features', X.shape[1])
        mlflow.log_param('feature_names', str(FEATURE_NAMES))
        
        for name, pipeline in models.items():
            metrics, trained = train_and_evaluate(name, pipeline, X_train, X_test, y_train, y_test)
            results[name] = metrics
            
            if metrics['f1'] > best_f1:
                best_f1 = metrics['f1']
                best_model = trained
                best_name = name
        
        # Log best
        mlflow.log_param('best_model', best_name)
        mlflow.log_metric('best_f1', best_f1)
    
    # Save best model
    logger.info(f"\n✅ Best Model: {best_name} (F1={best_f1:.3f})")
    
    os.makedirs('ml_models/inference', exist_ok=True)
    joblib.dump(best_model, 'ml_models/inference/resume_matcher.pkl')
    
    metadata = {
        'best_model': best_name,
        'metrics': results[best_name],
        'all_results': results,
        'features': FEATURE_NAMES,
        'training_samples': len(X_train),
    }
    with open('ml_models/inference/model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Model saved to ml_models/inference/resume_matcher.pkl")
    return best_model, results

if __name__ == '__main__':
    run_training_pipeline()

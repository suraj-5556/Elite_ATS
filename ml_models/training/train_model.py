"""
TalentAI - MLflow Training Pipeline
Trains a Gradient Boosting classifier on synthetic resume data and saves
the model to ml_models/inference/ for production inference.

Run: python -m ml_models.training.train_model

MLOps Features:
- Tracks experiments in MLflow
- Logs hyperparameters, metrics, and artifacts
- Saves model for production inference
- Versioning via MLflow run_id
"""

import os
import sys
import pickle
import logging
import numpy as np
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def generate_synthetic_data(n_samples: int = 2000):
    """
    Generate synthetic training data representing resume features.
    
    Features:
        0: word_count_norm (0-2.0)
        1: keyword_overlap (0-1.0)
        2: section_coverage (0-1.0)
        3: metric_density (0-1.0)
        4: action_verb_score (0-1.0)
        5: length_quality (0-1.0)
        6: tech_density (0-1.0)
    
    Label: 1 = good match (should be shortlisted), 0 = poor match
    """
    np.random.seed(42)
    
    # Generate features with realistic distributions
    features = np.zeros((n_samples, 7))
    labels = np.zeros(n_samples, dtype=int)
    
    for i in range(n_samples):
        # Positive samples (good resumes) - ~50% of data
        if i < n_samples // 2:
            features[i] = [
                np.random.uniform(0.7, 1.5),  # good word count
                np.random.uniform(0.4, 0.9),  # high keyword overlap
                np.random.uniform(0.6, 1.0),  # many sections present
                np.random.uniform(0.4, 1.0),  # quantified achievements
                np.random.uniform(0.4, 1.0),  # strong action verbs
                np.random.uniform(0.8, 1.0),  # good length quality
                np.random.uniform(0.4, 1.0),  # tech terms
            ]
            labels[i] = 1
        else:
            # Negative samples (weak resumes)
            features[i] = [
                np.random.uniform(0.1, 0.6),  # too short/long
                np.random.uniform(0.0, 0.35), # low keyword overlap
                np.random.uniform(0.2, 0.6),  # missing sections
                np.random.uniform(0.0, 0.3),  # few metrics
                np.random.uniform(0.0, 0.3),  # weak action verbs
                np.random.uniform(0.2, 0.7),  # length issues
                np.random.uniform(0.0, 0.35), # low tech density
            ]
            labels[i] = 0
    
    # Add some noise for realism
    noise = np.random.normal(0, 0.05, features.shape)
    features = np.clip(features + noise, 0, 2.0)
    
    return features, labels


def train_model():
    """Full training pipeline with MLflow tracking."""
    try:
        import mlflow
        import mlflow.sklearn
    except ImportError:
        logger.error("MLflow not installed. Run: pip install mlflow")
        sys.exit(1)
    
    try:
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.model_selection import train_test_split, cross_val_score
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score,
            f1_score, roc_auc_score, classification_report
        )
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        logger.error("scikit-learn not installed. Run: pip install scikit-learn")
        sys.exit(1)

    # ── MLflow Setup ──────────────────────────────────────────────────────────
    tracking_uri = os.getenv('MLFLOW_TRACKING_URI', './mlruns')
    experiment_name = os.getenv('MLFLOW_EXPERIMENT_NAME', 'talentai-resume-screening')
    
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    
    logger.info(f"MLflow tracking URI: {tracking_uri}")
    logger.info(f"Experiment: {experiment_name}")

    # ── Generate Data ─────────────────────────────────────────────────────────
    logger.info("Generating synthetic training data...")
    X, y = generate_synthetic_data(n_samples=3000)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    logger.info(f"Train: {X_train.shape}, Test: {X_test.shape}")

    # ── Hyperparameters ───────────────────────────────────────────────────────
    hyperparams = {
        'n_estimators': 200,
        'max_depth': 4,
        'learning_rate': 0.1,
        'min_samples_split': 10,
        'min_samples_leaf': 5,
        'subsample': 0.8,
        'random_state': 42,
    }

    with mlflow.start_run(run_name=f"gb_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        # Log hyperparameters
        mlflow.log_params(hyperparams)
        mlflow.log_param('n_train_samples', X_train.shape[0])
        mlflow.log_param('n_test_samples', X_test.shape[0])
        mlflow.log_param('n_features', X_train.shape[1])
        mlflow.log_param('model_type', 'GradientBoostingClassifier')

        # ── Train ─────────────────────────────────────────────────────────────
        logger.info("Training Gradient Boosting classifier...")
        model = GradientBoostingClassifier(**hyperparams)
        model.fit(X_train, y_train)

        # ── Evaluate ──────────────────────────────────────────────────────────
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_prob),
        }

        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='roc_auc')
        metrics['cv_roc_auc_mean'] = cv_scores.mean()
        metrics['cv_roc_auc_std'] = cv_scores.std()

        mlflow.log_metrics(metrics)

        logger.info("\n" + "="*50)
        logger.info("TRAINING RESULTS")
        logger.info("="*50)
        for k, v in metrics.items():
            logger.info(f"  {k:25s}: {v:.4f}")
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, y_pred, target_names=['Poor', 'Good']))

        # Feature importance
        feature_names = [
            'word_count_norm', 'keyword_overlap', 'section_coverage',
            'metric_density', 'action_verb_score', 'length_quality', 'tech_density'
        ]
        for name, importance in zip(feature_names, model.feature_importances_):
            logger.info(f"  Feature {name:25s}: {importance:.4f}")
            mlflow.log_metric(f"fi_{name}", importance)

        # ── Save Model ─────────────────────────────────────────────────────────
        output_dir = os.path.join(
            os.path.dirname(__file__), '..', 'inference'
        )
        os.makedirs(output_dir, exist_ok=True)
        model_path = os.path.join(output_dir, 'gb_model.pkl')

        with open(model_path, 'wb') as f:
            pickle.dump(model, f)

        logger.info(f"\nModel saved to: {model_path}")
        mlflow.log_artifact(model_path)

        # Log model with MLflow
        mlflow.sklearn.log_model(model, "gradient_boosting_model")
        
        run_id = mlflow.active_run().info.run_id
        logger.info(f"MLflow run_id: {run_id}")
        logger.info("Training complete! ✅")

    return model_path


if __name__ == '__main__':
    train_model()

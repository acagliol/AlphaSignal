"""
XGBoost Model Training
Train binary classification model to predict next-day stock direction
"""

import xgboost as xgb
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.preprocessing import StandardScaler
from typing import Dict, Tuple, List
import joblib
import logging
import os

logger = logging.getLogger(__name__)


class XGBoostPredictor:
    """
    XGBoost model for predicting next-day stock direction
    """

    def __init__(self, model_path: str = None):
        self.model = None
        self.feature_names = None
        self.selected_features = None
        self.model_path = model_path or "models/xgboost_model.pkl"
        self.scaler = StandardScaler()

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_splits: int = 5,
        n_features: int = 40
    ) -> Dict[str, float]:
        """
        Train XGBoost with time-series cross-validation and feature selection

        CRITICAL: Use TimeSeriesSplit to avoid look-ahead bias
        """

        self.feature_names = list(X.columns)
        logger.info(f"Training with {len(self.feature_names)} features on {len(X)} samples")

        # Feature Selection - Keep only the best features
        logger.info(f"Performing feature selection to select top {n_features} features...")
        selector = SelectKBest(score_func=mutual_info_classif, k=min(n_features, len(self.feature_names)))
        X_selected = selector.fit_transform(X, y)

        # Get selected feature names
        feature_scores = pd.DataFrame({
            'feature': self.feature_names,
            'score': selector.scores_
        }).sort_values('score', ascending=False)

        self.selected_features = feature_scores.head(n_features)['feature'].tolist()
        logger.info(f"Selected top {len(self.selected_features)} features")
        logger.info(f"Top 10: {', '.join(self.selected_features[:10])}")

        # Use only selected features
        X = X[self.selected_features]
        self.feature_names = self.selected_features

        # Scale features
        X_scaled = pd.DataFrame(
            self.scaler.fit_transform(X),
            columns=X.columns,
            index=X.index
        )
        X = X_scaled

        # Optimized XGBoost parameters for better accuracy
        # Class weight to handle imbalance
        class_counts = y.value_counts()
        scale_pos_weight = class_counts[0] / class_counts[1] if len(class_counts) == 2 else 1

        params = {
            'objective': 'binary:logistic',
            'eval_metric': 'auc',
            'max_depth': 5,              # Allow more complex patterns
            'learning_rate': 0.08,       # Slightly faster learning
            'n_estimators': 400,         # More trees
            'subsample': 0.85,           # Higher sampling
            'colsample_bytree': 0.85,    # Use more features
            'min_child_weight': 3,       # Less restrictive
            'gamma': 0.2,                # Moderate pruning
            'reg_alpha': 0.05,           # Lighter L1 regularization
            'reg_lambda': 1.0,           # Moderate L2 regularization
            'scale_pos_weight': scale_pos_weight,  # Handle class imbalance
            'random_state': 42,
            'early_stopping_rounds': 25
        }

        logger.info(f"Class balance - UP: {class_counts.get(1, 0)}, DOWN: {class_counts.get(0, 0)}")
        logger.info(f"Scale pos weight: {scale_pos_weight:.2f}")

        # Time-series cross-validation
        tscv = TimeSeriesSplit(n_splits=n_splits)

        cv_results = []

        logger.info(f"Starting {n_splits}-fold time-series cross-validation...")

        for fold, (train_idx, val_idx) in enumerate(tscv.split(X), 1):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            # Train model
            model = xgb.XGBClassifier(**params)
            model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                verbose=False
            )

            # Predictions
            y_pred = model.predict(X_val)
            y_pred_proba = model.predict_proba(X_val)[:, 1]

            # Metrics
            accuracy = accuracy_score(y_val, y_pred)
            precision = precision_score(y_val, y_pred, zero_division=0)
            recall = recall_score(y_val, y_pred, zero_division=0)
            auc = roc_auc_score(y_val, y_pred_proba)

            cv_results.append({
                'fold': fold,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'auc': auc
            })

            logger.info(f"Fold {fold}/{n_splits}: Acc={accuracy:.4f}, Precision={precision:.4f}, Recall={recall:.4f}, AUC={auc:.4f}")

        # Train final model on all data (without early stopping)
        logger.info("Training final model on all data...")
        final_params = params.copy()
        final_params.pop('early_stopping_rounds', None)  # Remove early stopping for final model
        self.model = xgb.XGBClassifier(**final_params)
        self.model.fit(X, y, verbose=False)

        # Save model
        self._save_model()

        # Aggregate results
        cv_df = pd.DataFrame(cv_results)
        final_results = {
            'cv_accuracy_mean': cv_df['accuracy'].mean(),
            'cv_accuracy_std': cv_df['accuracy'].std(),
            'cv_precision_mean': cv_df['precision'].mean(),
            'cv_recall_mean': cv_df['recall'].mean(),
            'cv_auc_mean': cv_df['auc'].mean(),
            'cv_auc_std': cv_df['auc'].std(),
            'n_features': len(self.feature_names),
            'n_samples': len(X)
        }

        logger.info(f"✅ Training complete: Accuracy={final_results['cv_accuracy_mean']:.4f} ± {final_results['cv_accuracy_std']:.4f}, AUC={final_results['cv_auc_mean']:.4f} ± {final_results['cv_auc_std']:.4f}")

        return final_results

    def predict(self, X: pd.DataFrame) -> Dict[str, any]:
        """Make prediction on new data"""

        if self.model is None:
            self._load_model()

        # Ensure features match training (selected features only)
        X = X[self.feature_names]

        # Scale features
        X_scaled = pd.DataFrame(
            self.scaler.transform(X),
            columns=X.columns,
            index=X.index
        )

        # Predict
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]

        return {
            'prediction': 'UP' if prediction == 1 else 'DOWN',
            'probability_up': float(probabilities[1]),
            'probability_down': float(probabilities[0]),
            'confidence': float(max(probabilities))
        }

    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance scores"""

        if self.model is None:
            raise ValueError("Model not trained")

        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        return importance_df

    def _save_model(self):
        """Save trained model"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'feature_names': self.feature_names,
            'scaler': self.scaler
        }, self.model_path)
        logger.info(f"💾 Model saved to {self.model_path}")

    def _load_model(self):
        """Load saved model"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}")

        data = joblib.load(self.model_path)
        self.model = data['model']
        self.feature_names = data['feature_names']
        self.scaler = data.get('scaler', StandardScaler())  # Backward compatibility
        logger.info(f"📂 Model loaded from {self.model_path}")

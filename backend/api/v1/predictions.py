"""
Predictions API Routes
ML-powered stock direction predictions
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import pandas as pd
import logging

from database import get_db
from models import Predictions, SentimentData
from schemas import prediction_schema
from services.ml_engine.feature_engineering import FeatureEngineer
from services.ml_engine.model_training import XGBoostPredictor
from services.data_ingestion.market_data import MarketDataService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/predictions/{ticker}", response_model=List[prediction_schema.PredictionResponse])
async def get_predictions(
    ticker: str,
    days: int = Query(default=30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Get historical predictions for ticker"""
    cutoff_date = datetime.now() - timedelta(days=days)

    predictions = db.query(Predictions)\
        .filter(
            Predictions.ticker == ticker.upper(),
            Predictions.prediction_date >= cutoff_date
        )\
        .order_by(Predictions.prediction_date.desc())\
        .all()

    if not predictions:
        raise HTTPException(status_code=404, detail=f"No predictions found for {ticker}")

    return predictions


@router.post("/predictions/{ticker}/predict")
async def make_prediction(
    ticker: str,
    db: Session = Depends(get_db)
):
    """
    Generate prediction for ticker
    Uses latest data and trained ML model
    """

    try:
        # Load trained model
        model = XGBoostPredictor(model_path='models/xgboost_model.pkl')

        # Fetch latest data
        market_service = MarketDataService()
        price_df = market_service.fetch_prices(ticker, start_date=None, end_date=None)

        if price_df.empty:
            raise HTTPException(status_code=404, detail=f"No price data found for {ticker}")

        # Get sentiment data (optional)
        sentiment_data = db.query(SentimentData)\
            .filter(SentimentData.ticker == ticker.upper())\
            .all()

        sentiment_df = pd.DataFrame([{
            'date': s.date,
            'sentiment_score': s.sentiment_score,
            'article_count': s.article_count
        } for s in sentiment_data]) if sentiment_data else None

        # Engineer features
        engineer = FeatureEngineer()
        features_df = engineer.create_features(price_df, sentiment_df)

        if features_df.empty:
            raise HTTPException(status_code=500, detail="Failed to engineer features")

        # Get latest features
        feature_names = engineer.get_feature_names(features_df)
        latest_features = features_df.iloc[-1:][feature_names]

        # Make prediction
        prediction_result = model.predict(latest_features)

        # Save to database
        prediction_entry = Predictions(
            ticker=ticker.upper(),
            prediction_date=datetime.now().date(),
            target_date=(datetime.now() + timedelta(days=1)).date(),
            predicted_direction=prediction_result['prediction'],
            probability_up=prediction_result['probability_up'],
            probability_down=prediction_result['probability_down'],
            confidence=prediction_result['confidence'],
            model_version="xgboost_v1"
        )

        db.add(prediction_entry)
        db.commit()
        db.refresh(prediction_entry)

        logger.info(f"Generated prediction for {ticker}: {prediction_result['prediction']} ({prediction_result['confidence']:.2%} confidence)")

        return {
            "ticker": ticker,
            "prediction_date": str(prediction_entry.prediction_date),
            "prediction": prediction_result['prediction'],
            "probability_up": prediction_result['probability_up'],
            "probability_down": prediction_result['probability_down'],
            "confidence": prediction_result['confidence'],
            "message": "Prediction generated successfully"
        }

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="ML model not found. Please train the model first.")
    except Exception as e:
        logger.error(f"Error making prediction for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/{ticker}/accuracy")
async def get_prediction_accuracy(
    ticker: str,
    days: int = Query(default=90, ge=30, le=365),
    db: Session = Depends(get_db)
):
    """
    Calculate prediction accuracy for ticker
    Compares predictions to actual outcomes
    """
    cutoff_date = datetime.now() - timedelta(days=days)

    predictions = db.query(Predictions)\
        .filter(
            Predictions.ticker == ticker.upper(),
            Predictions.prediction_date >= cutoff_date,
            Predictions.actual_direction.isnot(None)
        )\
        .all()

    if not predictions:
        raise HTTPException(status_code=404, detail="No predictions with actual outcomes found")

    total = len(predictions)
    correct = sum(1 for p in predictions if p.correct)
    accuracy = (correct / total) * 100

    # Calculate by confidence bucket
    high_conf = [p for p in predictions if p.confidence > 0.7]
    medium_conf = [p for p in predictions if 0.6 <= p.confidence <= 0.7]
    low_conf = [p for p in predictions if p.confidence < 0.6]

    return {
        "ticker": ticker,
        "total_predictions": total,
        "correct_predictions": correct,
        "accuracy_pct": round(accuracy, 2),
        "high_confidence": {
            "count": len(high_conf),
            "accuracy": round((sum(1 for p in high_conf if p.correct) / len(high_conf) * 100), 2) if high_conf else 0
        },
        "medium_confidence": {
            "count": len(medium_conf),
            "accuracy": round((sum(1 for p in medium_conf if p.correct) / len(medium_conf) * 100), 2) if medium_conf else 0
        },
        "low_confidence": {
            "count": len(low_conf),
            "accuracy": round((sum(1 for p in low_conf if p.correct) / len(low_conf) * 100), 2) if low_conf else 0
        }
    }

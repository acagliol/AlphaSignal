"""
Prediction Schemas
"""

from pydantic import BaseModel
from datetime import date
from typing import Optional, Dict, Any


class PredictionResponse(BaseModel):
    id: int
    ticker: str
    prediction_date: date
    target_date: date
    predicted_direction: str
    probability_up: float
    probability_down: float
    confidence: float
    actual_direction: Optional[str] = None
    correct: Optional[bool] = None
    model_version: str

    class Config:
        from_attributes = True


class PredictionCreate(BaseModel):
    ticker: str
    days: Optional[int] = 365

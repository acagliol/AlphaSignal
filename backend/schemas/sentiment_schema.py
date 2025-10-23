"""
Sentiment Data Schemas
"""

from pydantic import BaseModel
from datetime import date
from typing import Optional


class SentimentResponse(BaseModel):
    id: int
    ticker: str
    date: date
    sentiment_score: float
    article_count: int
    positive_count: Optional[int] = 0
    negative_count: Optional[int] = 0
    neutral_count: Optional[int] = 0
    source: str

    class Config:
        from_attributes = True

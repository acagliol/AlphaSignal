"""
News Sentiment Analyzer
Scrape financial news and compute sentiment scores
"""

import requests
from textblob import TextBlob
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class NewsSentimentAnalyzer:
    """
    Scrape financial news and compute sentiment scores
    Using Financial Modeling Prep API (free tier: 250 calls/day)
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://financialmodelingprep.com/api/v3"

    def get_news(self, ticker: str, days: int = 30) -> List[Dict]:
        """Fetch news articles for ticker"""
        url = f"{self.base_url}/stock_news"
        params = {
            "tickers": ticker,
            "limit": 100,
            "apikey": self.api_key
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            articles = response.json()

            # Filter by date
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered = [
                article for article in articles
                if datetime.fromisoformat(article['publishedDate'].replace('Z', '+00:00')) > cutoff_date
            ]

            logger.info(f"Fetched {len(filtered)} articles for {ticker}")
            return filtered

        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {e}")
            return []

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using TextBlob
        Returns: polarity (-1 to +1), subjectivity (0 to 1)
        """
        blob = TextBlob(text)
        return {
            "polarity": blob.sentiment.polarity,
            "subjectivity": blob.sentiment.subjectivity
        }

    def process_articles(self, articles: List[Dict]) -> pd.DataFrame:
        """Process articles into daily sentiment scores"""
        data = []

        for article in articles:
            # Combine title and text
            text = article['title'] + " " + article.get('text', '')

            # Analyze sentiment
            sentiment = self.analyze_sentiment(text)

            # Extract date
            date = datetime.fromisoformat(
                article['publishedDate'].replace('Z', '+00:00')
            ).date()

            data.append({
                'date': date,
                'polarity': sentiment['polarity'],
                'subjectivity': sentiment['subjectivity'],
                'title': article['title']
            })

        df = pd.DataFrame(data)

        if df.empty:
            return df

        # Aggregate by day
        daily = df.groupby('date').agg({
            'polarity': 'mean',
            'subjectivity': 'mean',
            'title': 'count'  # Article count
        }).reset_index()

        daily.rename(columns={'title': 'article_count'}, inplace=True)

        # Classify sentiment
        daily['sentiment_label'] = daily['polarity'].apply(
            lambda x: 'positive' if x > 0.1 else ('negative' if x < -0.1 else 'neutral')
        )

        return daily

    def calculate_correlation(
        self,
        sentiment_df: pd.DataFrame,
        price_df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Calculate correlation between sentiment and next-day returns
        """
        # Merge sentiment with prices
        merged = sentiment_df.merge(
            price_df[['date', 'close']],
            on='date',
            how='inner'
        )

        if len(merged) < 10:
            return {"correlation": 0.0, "pvalue": 1.0, "n_samples": len(merged)}

        # Calculate next-day returns
        merged['next_return'] = merged['close'].pct_change().shift(-1)

        # Drop NaN
        merged = merged.dropna()

        # Calculate Pearson correlation
        from scipy.stats import pearsonr
        correlation, pvalue = pearsonr(
            merged['polarity'],
            merged['next_return']
        )

        return {
            "correlation": float(correlation),
            "pvalue": float(pvalue),
            "n_samples": len(merged),
            "significant": pvalue < 0.05
        }

"""
Reddit Social Signal Scraper
Scrape r/wallstreetbets for stock mentions and sentiment
"""

import praw
import pandas as pd
from datetime import datetime, timedelta
from textblob import TextBlob
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class RedditSignalScraper:
    """
    Scrape r/wallstreetbets for stock mentions and sentiment
    """

    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.subreddit = self.reddit.subreddit('wallstreetbets')

    def search_ticker(self, ticker: str, days: int = 30, limit: int = 100) -> List[Dict]:
        """Search for ticker mentions"""
        posts = []
        cutoff_time = datetime.now() - timedelta(days=days)

        try:
            for post in self.subreddit.search(ticker, time_filter='month', limit=limit):
                post_time = datetime.fromtimestamp(post.created_utc)

                if post_time < cutoff_time:
                    continue

                # Analyze sentiment
                sentiment = TextBlob(post.title + " " + post.selftext).sentiment

                posts.append({
                    'date': post_time.date(),
                    'title': post.title,
                    'score': post.score,
                    'num_comments': post.num_comments,
                    'sentiment': sentiment.polarity,
                    'url': post.url
                })

            logger.info(f"Found {len(posts)} Reddit posts for {ticker}")
            return posts

        except Exception as e:
            logger.error(f"Error scraping Reddit for {ticker}: {e}")
            return []

    def aggregate_daily(self, posts: List[Dict]) -> pd.DataFrame:
        """Aggregate posts by day"""
        if not posts:
            return pd.DataFrame()

        df = pd.DataFrame(posts)

        daily = df.groupby('date').agg({
            'score': 'sum',           # Total upvotes
            'num_comments': 'sum',    # Total comments
            'sentiment': 'mean',      # Average sentiment
            'title': 'count'          # Mention count
        }).reset_index()

        daily.rename(columns={'title': 'mention_count'}, inplace=True)

        # Detect "spikes" (mentions > 2x average)
        avg_mentions = daily['mention_count'].mean()
        daily['is_spike'] = daily['mention_count'] > (avg_mentions * 2)

        return daily

"""
Database models package.

Exports all database models for easy importing.
"""
from app.models.base import Base, TimestampMixin
from app.models.user import User
from app.models.data_point import DataPoint, SeriesMetadata
from app.models.fred_data import FredDataPoint
from app.models.newsletter import Newsletter
from app.models.article import Article
from app.models.article_source import ArticleSource
from app.models.article_bookmark import ArticleBookmark
from app.models.bookmark_list import BookmarkList

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "DataPoint",
    "SeriesMetadata",
    "FredDataPoint",
    "Newsletter",
    "Article",
    "ArticleSource",
    "ArticleBookmark",
    "BookmarkList",
]

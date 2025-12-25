"""
Repositories Package

Data access layer for Review Radar system.
"""

from .base_repository import BaseRepository
from .review_repository import ReviewRepository

__all__ = [
    'BaseRepository',
    'ReviewRepository',
]

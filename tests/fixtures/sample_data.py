"""
Sample test data for tests

Provides reusable test data across test suite.
"""

import pandas as pd
from datetime import datetime


def get_sample_reviews(count: int = 3, with_labels: bool = False):
    """
    Get sample reviews DataFrame
    
    Args:
        count: Number of reviews to generate
        with_labels: Include labels or not
    
    Returns:
        DataFrame with sample reviews
    """
    data = {
        'review_id': list(range(1, count + 1)),
        'batch_id': [100] * count,
        'review': [
            'อาหารอร่อยมาก บริการดีมาก',
            'ราคาแพงไปหน่อย แต่คุ้มค่า',
            'บรรยากาศดี เหมาะกับครอบครัว'
        ][:count],
        'source': ['Facebook', 'Twitter', 'Instagram'][:count],
        'review_date': [datetime.now()] * count,
        'created_at': [datetime.now()] * count,
        'updated_at': [datetime.now()] * count,
    }
    
    if with_labels:
        data['labels'] = [
            {
                'aspects': {
                    'food': {'mentioned': True, 'sentiment': 'positive', 'confidence': 0.95},
                    'service': {'mentioned': True, 'sentiment': 'positive', 'confidence': 0.90}
                }
            },
            {
                'aspects': {
                    'price': {'mentioned': True, 'sentiment': 'negative', 'confidence': 0.85}
                }
            },
            {
                'aspects': {
                    'ambiance': {'mentioned': True, 'sentiment': 'positive', 'confidence': 0.92}
                }
            }
        ][:count]
    else:
        data['labels'] = [None] * count
    
    return pd.DataFrame(data)


def get_sample_batch(batch_id: int = 100):
    """Get sample batch data"""
    return {
        'batch_id': batch_id,
        'customer_id': 1,
        'title': 'Restaurant Review Analysis',
        'description': 'Analyze customer reviews for new restaurant',
        'aspects': 'food,service,price,ambiance,location',
        'status': 'in_progress',
        'report_consent': True,
        'train_consent': True,
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }


SAMPLE_ASPECTS = ['food', 'service', 'price', 'ambiance', 'location']


SAMPLE_LABEL_RESULT = {
    'aspects': {
        'food': {
            'mentioned': True,
            'sentiment': 'positive',
            'confidence': 0.95,
            'snippet': 'อาหารอร่อยมาก'
        },
        'service': {
            'mentioned': True,
            'sentiment': 'positive',
            'confidence': 0.90,
            'snippet': 'บริการดีมาก'
        }
    },
    'overall_sentiment': 'positive',
    'labeling_metadata': {
        'provider': 'gemini-flash-2.0',
        'timestamp': '2025-12-24T10:00:00Z',
        'cost': 0.0001,
        'processing_time_ms': 150,
        'validation_passed': True
    }
}

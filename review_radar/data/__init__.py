"""Data handling module for Review Radar ABSA system"""

from .base_client import BaseClient
from .supabase_client import SupabaseClient, create_supabase_client_from_env
from .client_factory import ClientFactory

__all__ = ['BaseClient', 'SupabaseClient', 'ClientFactory', 'create_supabase_client_from_env']

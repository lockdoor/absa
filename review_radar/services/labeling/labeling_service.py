"""
Labeling Service - Main Orchestrator

Orchestrates the auto-labeling workflow:
1. Fetch unlabeled reviews
2. Send to LLM provider
3. Validate labels
4. Save to database
5. Track metrics
"""

# from typing import Optional, Dict, List, Any
# from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import logging
from typing import Optional, Dict, List, Any

from .providers.base_provider import BaseLabelingProvider, LabelResult
from review_radar.repositories.review_repository import ReviewRepository
from review_radar.repositories.batch_repository import BatchRepository
from review_radar.repositories.label_repository import LabelRepository
from review_radar.services.labeling.providers.provider_factory import ProviderFactory
from review_radar.services.labeling.providers.gemini_flash_lite_2_5_provider import GeminiFlashLite25Provider
# from review_radar.utils import setup_logger


class LabelingService:

    def __init__(self, batch_id: int, provider: str, 
                 client_type: str, logger: Optional[logging.Logger]=None):
        self.batch_id = batch_id
        # self.provider = provider
        self.client_type = client_type
        self.logger = logger
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0

        # Initialize repositories
        self.review_repo = ReviewRepository(client_type=client_type, logger=self.logger)
        self.batch_repo = BatchRepository(client_type=client_type, logger=self.logger)
        self.label_repo = LabelRepository(client_type=client_type, logger=self.logger)

        self.appects = self.batch_repo.get_batch_aspects(batch_id=batch_id)

        # will use factory pattern later to support multiple providers
        # self.provider: GeminiFlashLite25Provider = GeminiFlashLite25Provider(
        #     aspects=self.appects,
        #     logger=self.logger
        # )
        self.provider: BaseLabelingProvider = ProviderFactory.create(
            provider=provider,
            aspects=self.appects,
            logger=self.logger
        )

    def _log(self, message: str, level: str = "info", **kwargs):
        """Helper method for logging"""
        if self.logger:
            log_method = getattr(self.logger, level, self.logger.info)
            log_method(message, extra=kwargs)

    def reset_counters(self):
        """Reset token and request counters"""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0

    def update_log(self, status: str = "successed"):
        """
        Update labeling report for a batch
        This function read CSV log file if exists and update the report in the database.
        """
        
        report_dict: dict = {
            'status': status, 
            'input_tokens': self.total_input_tokens, 
            'output_tokens': self.total_output_tokens,
            'total_requests': self.total_requests,
            'timestamp': datetime.now().isoformat()}
        try:
            # Read existing log file
            log_df = pd.read_csv(f"labeling_batch_{self.batch_id}_log.csv")
            log_df = pd.concat([log_df, pd.DataFrame(report_dict, index=[0])], ignore_index=True)

        except FileNotFoundError:
            # Create empty DataFrame if log file does not exist
            log_df = pd.DataFrame(report_dict, index=[0])
        finally:
            # Save updated log file
            log_df.to_csv(f"labeling_batch_{self.batch_id}_log.csv", index=False)

    def make_labels(
            self,
            fecth_limit: int = 100,
            batch_size: int = 20,
            input_token_limit: int = 1000000,
            output_token_limit: int = 1000000) -> None:

        for i in range(0, 10000):  # Arbitrary large number to ensure all reviews are processed
            
            reviews = self.review_repo.get_unlabeled_reviews(
                batch_id=self.batch_id,
                limit=fecth_limit,
                offset=i * fecth_limit)
            
            if not reviews:
                self._log("No more unlabeled reviews to process.", level="info")
                self.update_log(status="completed")
                break  # No more reviews to process

            results_label: list = [] # [{review_id: int, label: LabelResult}, ...]

            try: 
                for review in reviews:
                    try:
                        label: LabelResult =  self.provider.process_label(review['review'])
                    except Exception as e:
                        self._log(f"Error processing review ID {review['id']}: {e}", level="error")
                        return  # Skip to next review

                    # Update token counts
                    # This instruction may raise KeyError if metadata is missing
                    self.total_input_tokens += label.metadata['usage_metadata']['prompt_token_count']
                    self.total_output_tokens += label.metadata['usage_metadata']['candidates_token_count']
                    self.total_requests += 1
                    results_label.append({
                        'review_id': review['id'],
                        'label': label.to_dict()})

                    # Save to database in batches
                    if len(results_label) >= batch_size:
                        self._log(f"LabelResult limit reached of {batch_size}, upload to databese")
                        self.label_repo.insert_labels_batch(labels=results_label)
                        results_label = []

                    # Check token limits
                    if (self.total_input_tokens > input_token_limit) or (self.total_output_tokens > output_token_limit):
                        self._log("Token limit reached, stopping labeling process.", level="info")
                        self.update_log(status="stopped_due_to_token_limit")
                        return
                        
            except KeyError as e:
                self._log(f"KeyError during labeling: {e}", level="error")
                self.update_log(status="failed_due_to_keyerror")
                return
            
            finally:
                # Insert any remaining labels
                if results_label:
                    self._log(f"Rest of LabelResult: {len(results_label)}, upload to databese")
                    self.label_repo.insert_labels_batch(labels=results_label)
                self.reset_counters()

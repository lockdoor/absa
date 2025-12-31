from typing import Optional
import logging

from .gemini_flash_lite_2_5_provider import GeminiFlashLite25Provider
from .base_provider import BaseLabelingProvider


class ProviderFactory:

    _instances: dict[str, BaseLabelingProvider] = {
        'gemini-2.5-flash-lite': GeminiFlashLite25Provider
    }

    def _log(self, message: str, level: str = "info", **kwargs):
        """Helper method for logging"""
        if self.logger:
            log_method = getattr(self.logger, level, self.logger.info)
            log_method(message, extra=kwargs)

    @classmethod
    def models_info(cls) -> list[str]:
        """Return available provider models"""
        return list(ProviderFactory._instances.keys())

    @classmethod
    def create(
        cls,
        provider: str,
        aspects: list[str],
        logger: Optional[logging.Logger] = None) -> BaseLabelingProvider:
        """
        สร้าง LabelingProvider instance

        Args:
            provider: provider model type eg. 'gemini-2.5-flash-lite'
            logger: Optional logger

        Returns:
            LabelingProvider instance
        """
        try:
            provider_class = ProviderFactory._instances[provider]
            return provider_class(aspects=aspects, logger=logger)
        except KeyError:
            cls._log(f"Provider factory error: Invalid provider: {provider}", level="error")
            raise ValueError(f"Invalid provider: {provider}. Must be one of {list(ProviderFactory._instances.keys())}")

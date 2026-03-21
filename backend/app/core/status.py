"""Centralized status type definitions for all entities.

This module provides type-safe status values using StrEnum
to prevent typos and ensure consistency across the codebase.
"""
from enum import StrEnum


class AssetStatus(StrEnum):
    """Status values for MarketingAsset entities."""
    UPLOADED = "uploaded"
    COMPLETED = "completed"
    FAILED = "failed"
    RECEIVED = "received"


class EnrichmentJobStatus(StrEnum):
    """Status values for EnrichmentJob entities."""
    PENDING = "pending"
    COMPLETED = "completed"


class CampaignSequenceStatus(StrEnum):
    """Status values for CampaignSequence entities."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class N8nShredderCallbackStatus(StrEnum):
    """Status values for n8n webhook callback responses."""
    SUCCESS = "success"
    FAILED = "failed"


class ResponseStatus(StrEnum):
    """Status values for API response messages."""
    ACCEPTED = "accepted"
    RECEIVED = "received"

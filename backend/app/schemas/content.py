"""Pydantic schemas for ContentSnack model."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from .base import BaseSchema


class ContentSnackResponse(BaseSchema):
    """Schema for returning ContentSnack data."""
    
    id: UUID = Field(..., description="Unique identifier for the content snack")
    asset_id: UUID = Field(..., description="Parent asset identifier")
    content_type: str = Field(..., description="Content type (linkedin_post or email_pill)")
    content_text: str = Field(..., description="The actual content text")
    metadata: Optional[dict] = Field(None, description="Additional metadata (hashtags, target audience, etc.)")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class AssetContentResponse(BaseSchema):
    """Schema for returning all content for a specific asset."""
    
    asset_id: UUID = Field(..., description="Unique identifier for the marketing asset")
    content_items: List[ContentSnackResponse] = Field(
        default_factory=list,
        description="List of content items (LinkedIn posts and email pills)"
    )
    total_count: int = Field(..., description="Total number of content items")
    linkedin_post_count: int = Field(..., description="Number of LinkedIn posts")
    email_pill_count: int = Field(..., description="Number of email pills")

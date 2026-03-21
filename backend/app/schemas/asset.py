"""Pydantic schemas for MarketingAsset model."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import ConfigDict, Field

from app.core.status import AssetStatus, N8nShredderCallbackStatus
from app.schemas.base import BaseSchema
from app.schemas.content import ContentSnackResponse


# Base schema with common fields
class MarketingAssetBase(BaseSchema):
    """Base schema for MarketingAsset."""
    
    filename: str = Field(..., min_length=1, max_length=255, description="Sequential filename (e.g., 001.pdf)")
    original_filename: Optional[str] = Field(None, max_length=255, description="Original filename before sequential renaming")
    sequence_number: Optional[int] = Field(None, description="Sequential number for file naming")
    storage_url: str = Field(..., min_length=1, max_length=500, description="Storage URL path")
    status: AssetStatus = Field(AssetStatus.UPLOADED, description="Current status of the asset")
    
    # JSONB webhook payload
    webhook_payload: Optional[dict] = Field(None, description="Webhook callback data")


# Schema for creating a new asset
class MarketingAssetCreate(MarketingAssetBase):
    """Schema for creating a new MarketingAsset."""
    
    model_config = ConfigDict(extra="forbid")


# Schema for updating an existing asset
class MarketingAssetUpdate(BaseSchema):
    """Schema for updating a MarketingAsset."""
    
    status: Optional[AssetStatus] = Field(None, description="Updated status")
    webhook_payload: Optional[dict] = Field(None, description="Updated webhook payload")
    
    model_config = ConfigDict(extra="forbid")


# Schema for reading an asset (includes read-only fields)
class MarketingAssetResponse(MarketingAssetBase):
    """Schema for returning MarketingAsset data."""
    
    id: UUID = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


# Schema for upload response
class AssetUploadResponse(BaseSchema):
    """Schema for asset upload response."""
    
    asset_id: UUID = Field(..., description="Unique identifier for the uploaded asset")
    filename: str = Field(..., description="Sequential filename (e.g., 001.pdf)")
    original_filename: Optional[str] = Field(None, description="Original filename before sequential renaming")
    sequence_number: Optional[int] = Field(None, description="Sequential number for file naming")
    storage_url: str = Field(..., description="Storage URL path")
    status: AssetStatus = Field(..., description="Current status")
    message: str = Field(..., description="Upload status message")


# Schema for n8n shredder callback
class N8nShredderCallback(BaseSchema):
    """Schema for n8n shredder webhook callback."""
    
    asset_id: UUID = Field(..., description="Unique identifier for the marketing asset")
    status: N8nShredderCallbackStatus = Field(..., description="Callback status")
    linkedin_posts: List[str] = Field(
        default_factory=list,
        description="List of LinkedIn post content strings"
    )
    email_pills: List[str] = Field(
        default_factory=list,
        description="List of email pill content strings"
    )


# Schema for asset with snacks response
class AssetWithSnacksResponse(BaseSchema):
    """Schema for returning MarketingAsset with all its ContentSnacks."""
    
    asset: MarketingAssetResponse = Field(..., description="Marketing asset data")
    snacks: List[ContentSnackResponse] = Field(..., description="List of content snacks")

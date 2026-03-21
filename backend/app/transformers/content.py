"""Transformer for ContentSnack data."""
from typing import List
from uuid import UUID

from app.models.content_snack import ContentSnack
from app.schemas.content import ContentSnackResponse, AssetContentResponse


def transform_content_snack(content_snack: ContentSnack) -> ContentSnackResponse:
    """Transform a ContentSnack model instance into a ContentSnackResponse schema.
    
    Args:
        content_snack: The ContentSnack model instance from the database
        
    Returns:
        ContentSnackResponse: Validated and structured content data
    """
    return ContentSnackResponse(
        id=content_snack.id,
        asset_id=content_snack.asset_id,
        content_type=content_snack.content_type,
        content_text=content_snack.content_text,
        content_metadata=content_snack.content_metadata,
        created_at=content_snack.created_at,
        updated_at=content_snack.updated_at,
    )


def transform_asset_content(
    asset_id: UUID,
    content_items: List[ContentSnack],
) -> AssetContentResponse:
    """Transform a list of ContentSnack models into an AssetContentResponse.
    
    Args:
        asset_id: The UUID of the marketing asset
        content_items: List of ContentSnack model instances from the database
        
    Returns:
        AssetContentResponse: Validated and structured content data for the asset
    """
    # Transform each content item
    transformed_items = [transform_content_snack(item) for item in content_items]
    
    # Count content types
    linkedin_post_count = sum(1 for item in content_items if item.content_type == "linkedin_post")
    email_pill_count = sum(1 for item in content_items if item.content_type == "email_pill")
    
    return AssetContentResponse(
        asset_id=asset_id,
        content_items=transformed_items,
        total_count=len(content_items),
        linkedin_post_count=linkedin_post_count,
        email_pill_count=email_pill_count,
    )

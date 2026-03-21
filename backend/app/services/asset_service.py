"""Service layer for handling asset operations."""
import logging
from pathlib import Path
from typing import List, Tuple
from uuid import UUID, uuid4

from fastapi import HTTPException, status, UploadFile
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.status import AssetStatus, ResponseStatus
from app.models.asset import MarketingAsset
from app.models.content_snack import ContentSnack
from app.schemas.asset import (
    AssetUploadResponse,
    AssetWithSnacksResponse,
    ContentSnackResponse,
    MarketingAssetResponse,
    N8nShredderCallback,
)
from app.schemas.content import AssetContentResponse
from app.services.n8n_service import N8nService
from app.transformers.content import transform_asset_content

logger = logging.getLogger(__name__)


class AssetService:
    """Service for handling asset operations including upload and n8n callback processing."""
    
    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session.
        
        Args:
            db: Async database session.
        """
        self.db = db
        self.storage_dir = Path(settings.storage_dir)
    
    async def upload_asset(
        self,
        file: UploadFile,
        public_base_url: str,
    ) -> Tuple[MarketingAsset, AssetUploadResponse]:
        """Upload a PDF asset and create a MarketingAsset record.
        
        This method:
        1. Validates the uploaded file is a PDF
        2. Saves the file to the storage directory
        3. Creates a MarketingAsset record in the database
        4. Returns the asset and response data
        
        Args:
            file: UploadFile object containing the PDF
            public_base_url: Base URL for constructing storage URLs
            
        Returns:
            Tuple of (MarketingAsset, AssetUploadResponse)
            
        Raises:
            HTTPException: If file validation fails or database operation fails
        """
        try:
            # Validate file type
            if not file.filename or not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only PDF files are allowed",
                )
            
            # Ensure storage directory exists
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            
            # Get next sequence number
            result = await self.db.execute(
                select(func.coalesce(func.max(MarketingAsset.sequence_number), 0))
            )
            next_sequence = result.scalar() + 1
            
            # Generate sequential filename (001.pdf, 002.pdf, etc.)
            asset_id = uuid4()
            sequential_filename = f"{next_sequence:03d}.pdf"
            file_path = self.storage_dir / sequential_filename
            
            # Save file to storage
            try:
                contents = await file.read()
                with open(file_path, "wb") as f:
                    f.write(contents)
            except Exception as e:
                logger.error(f"Failed to save file {file.filename}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to save file: {str(e)}",
                )
            
            # Construct storage URL for static mount
            storage_url = f"/storage/pdfs/{sequential_filename}"
            
            # Create MarketingAsset record with original filename
            asset = MarketingAsset(
                id=asset_id,
                filename=sequential_filename,
                original_filename=file.filename,
                sequence_number=next_sequence,
                storage_url=storage_url,
                status=AssetStatus.UPLOADED,
            )
            
            self.db.add(asset)
            await self.db.commit()
            await self.db.refresh(asset)
            
            logger.info(f"Created asset {asset_id} for file {file.filename}")
            
            # Build full URL for n8n webhook using public_base_url
            full_file_url = f"{public_base_url}{storage_url}"
            
            # Trigger n8n content shredder webhook
            # Note: This should be called as a background task by the caller
            n8n_service = N8nService()
            await n8n_service.trigger_content_shredder(
                asset_id=asset_id,
                file_url=full_file_url,
            )
            
            # Build response
            response = AssetUploadResponse(
                asset_id=asset_id,
                filename=sequential_filename,
                original_filename=file.filename,
                sequence_number=next_sequence,
                storage_url=storage_url,
                status=AssetStatus.UPLOADED,
                message="PDF uploaded successfully and content shredder webhook triggered",
            )
            
            return asset, response
            
        except HTTPException:
            # Re-raise HTTPExceptions
            raise
        except Exception as e:
            logger.error(f"Failed to upload asset: {str(e)}", exc_info=True)
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload asset: {str(e)}",
            )
    
    async def process_n8n_callback(
        self,
        callback: N8nShredderCallback,
    ) -> dict:
        """Process n8n callback webhook with processing results.
        
        This method handles the callback from n8n content shredder with the
        processing status and creates ContentSnack records for each content item.
        
        Args:
            callback: N8nShredderCallback containing asset_id, status, and content lists
            
        Returns:
            dict: Success response with status "received"
            
        Raises:
            HTTPException: If asset is not found or update fails
        """
        try:
            # Find the asset by asset_id
            result = await self.db.execute(
                select(MarketingAsset).where(MarketingAsset.id == callback.asset_id)
            )
            asset = result.scalar_one_or_none()
            
            if not asset:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Asset with ID {callback.asset_id} not found",
                )
            
            # Process callback based on status
            if callback.status == "success":
                # Create ContentSnack records for LinkedIn posts
                for post_content in callback.linkedin_posts:
                    snack = ContentSnack(
                        asset_id=callback.asset_id,
                        content_type="linkedin_post",
                        content_text=post_content,
                    )
                    self.db.add(snack)
                
                # Create ContentSnack records for email pills
                for pill_content in callback.email_pills:
                    snack = ContentSnack(
                        asset_id=callback.asset_id,
                        content_type="email_pill",
                        content_text=pill_content,
                    )
                    self.db.add(snack)
                
                # Update asset status to completed
                asset.status = AssetStatus.COMPLETED
            else:
                # If status is "failed", update asset status accordingly
                asset.status = AssetStatus.FAILED
            
            # Commit all changes atomically
            await self.db.commit()
            
            logger.info(f"Processed n8n callback for asset {callback.asset_id} with status: {callback.status}")
            
            return {"status": ResponseStatus.RECEIVED}
            
        except HTTPException:
            # Re-raise HTTPExceptions
            raise
        except Exception as e:
            logger.error(f"Failed to process n8n callback: {str(e)}", exc_info=True)
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process n8n callback: {str(e)}",
            )
    
    async def get_asset_with_snacks(
        self,
        asset_id: str,
    ) -> AssetWithSnacksResponse:
        """Retrieve a marketing asset along with all its associated content snacks.
        
        Args:
            asset_id: UUID string of the asset
            
        Returns:
            AssetWithSnacksResponse: Asset data with list of content snacks
            
        Raises:
            HTTPException: If asset is not found or invalid ID format
        """
        try:
            # Validate asset_id
            try:
                asset_uuid = UUID(asset_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid asset ID format: {asset_id}",
                )
            
            # Find the asset with its snacks (using selectin for async loading)
            result = await self.db.execute(
                select(MarketingAsset)
                .where(MarketingAsset.id == asset_uuid)
                .options(selectinload(MarketingAsset.snacks))
            )
            asset = result.scalar_one_or_none()
            
            if not asset:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Asset with ID {asset_id} not found",
                )
            
            # Convert to response schema
            asset_response = MarketingAssetResponse.model_validate(asset)
            snacks_response = [ContentSnackResponse.model_validate(snack) for snack in asset.snacks]
            
            return AssetWithSnacksResponse(
                asset=asset_response,
                snacks=snacks_response,
            )
            
        except HTTPException:
            # Re-raise HTTPExceptions
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve asset with snacks: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve asset with snacks: {str(e)}",
            )
    
    async def get_asset_content(
        self,
        asset_id: str,
    ) -> AssetContentResponse:
        """Get cleaned content for a specific asset.
        
        This method retrieves all content items associated with a marketing asset
        and returns them in a clean, structured format ready for frontend consumption.
        
        Args:
            asset_id: The UUID of the marketing asset
            
        Returns:
            AssetContentResponse: Clean, structured content data for the asset
            
        Raises:
            HTTPException: If asset is not found or invalid ID format
        """
        try:
            # Validate asset_id is a valid UUID
            try:
                asset_uuid = UUID(asset_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid asset_id format: {asset_id}",
                )
            
            # Check if asset exists
            result = await self.db.execute(
                select(MarketingAsset).where(MarketingAsset.id == asset_uuid)
            )
            asset = result.scalar_one_or_none()
            
            if not asset:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Asset with ID {asset_id} not found",
                )
            
            # Fetch all content snacks for this asset
            result = await self.db.execute(
                select(ContentSnack)
                .where(ContentSnack.asset_id == asset_uuid)
                .order_by(ContentSnack.created_at)
            )
            content_items = result.scalars().all()
            
            # Transform to clean, structured format
            clean_content = transform_asset_content(asset_uuid, content_items)
            
            return clean_content
            
        except HTTPException:
            # Re-raise HTTPExceptions
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve asset content: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve asset content: {str(e)}",
            )

"""Assets router for PDF upload and processing."""
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.schemas.asset import AssetUploadResponse, N8nShredderCallback, AssetWithSnacksResponse
from app.schemas.content import AssetContentResponse
from app.services.asset_service import AssetService

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.post(
    "/upload",
    response_model=AssetUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload PDF asset for content recycling",
    description="Upload a PDF file and trigger the n8n content shredder webhook.",
)
async def upload_asset(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
) -> AssetUploadResponse:
    """
    Upload a PDF asset and trigger content shredder webhook.
    
    This endpoint:
    1. Validates the uploaded file is a PDF
    2. Saves the file to the storage/pdfs directory
    3. Creates a MarketingAsset record in the database
    4. Triggers the n8n content shredder webhook in the background
    5. Returns immediately with 202 Accepted status
    
    Args:
        file: UploadFile object containing the PDF
        background_tasks: FastAPI background tasks for async processing
        db: Async database session
    
    Returns:
        AssetUploadResponse: Asset details and upload status
    
    Raises:
        HTTPException: If file validation fails or database operation fails
    """
    try:
        # Initialize service
        service = AssetService(db)
        
        # Upload asset using service
        asset, response = await service.upload_asset(
            file=file,
            public_base_url=settings.public_base_url,
            background_tasks=background_tasks,
        )
        
        return response
        
    except HTTPException:
        # Re-raise HTTPExceptions
        raise
    except Exception as e:
        logger.error(f"Failed to upload asset: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload asset: {str(e)}",
        )


@router.post(
    "/webhook/n8n-callback",
    status_code=status.HTTP_200_OK,
    summary="Receive n8n callback webhook",
    description="Receive callback from n8n content shredder with processing results.",
)
async def receive_n8n_callback(
    callback: N8nShredderCallback,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Receive n8n callback webhook with processing results.
    
    This endpoint handles the callback from n8n content shredder with the
    processing status and creates ContentSnack records for each content item.
    
    Args:
        callback: N8nShredderCallback containing asset_id, status, and content lists
        db: Async database session
    
    Returns:
        dict: Success response with status "received"
    
    Raises:
        HTTPException: If asset is not found or update fails
    """
    try:
        # Initialize service
        service = AssetService(db)
        
        # Process callback using service
        result = await service.process_n8n_callback(callback)
        
        return result
        
    except HTTPException:
        # Re-raise HTTPExceptions
        raise
    except Exception as e:
        logger.error(f"Failed to process n8n callback: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process n8n callback: {str(e)}",
        )


@router.get(
    "/{asset_id}/snacks",
    response_model=AssetWithSnacksResponse,
    status_code=status.HTTP_200_OK,
    summary="Get asset with all content snacks",
    description="Retrieve a marketing asset along with all its associated content snacks.",
)
async def get_asset_with_snacks(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
) -> AssetWithSnacksResponse:
    """
    Retrieve a marketing asset along with all its associated content snacks.
    
    Args:
        asset_id: UUID string of the asset
        db: Async database session
    
    Returns:
        AssetWithSnacksResponse: Asset data with list of content snacks
    
    Raises:
        HTTPException: If asset is not found
    """
    try:
        service = AssetService(db)
        return await service.get_asset_with_snacks(asset_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve asset with snacks: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve asset with snacks: {str(e)}",
        )


@router.get(
    "/{asset_id}/content",
    response_model=AssetContentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get cleaned content for an asset",
    description="Retrieve all content items (LinkedIn posts and email pills) for a specific asset in a clean, structured format.",
)
async def get_asset_content(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
) -> AssetContentResponse:
    """
    Get cleaned content for a specific asset.
    
    This endpoint retrieves all content items associated with a marketing asset
    and returns them in a clean, structured format ready for frontend consumption.
    
    Args:
        asset_id: The UUID of the marketing asset
        db: Async database session
    
    Returns:
        AssetContentResponse: Clean, structured content data for the asset
    
    Raises:
        HTTPException: If asset is not found or database operation fails
    """
    try:
        service = AssetService(db)
        return await service.get_asset_content(asset_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve asset content: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve asset content: {str(e)}",
        )

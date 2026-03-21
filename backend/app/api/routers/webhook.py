"""Webhook router for receiving Clay webhook data."""
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.status import ResponseStatus
from app.models.enrichment import EnrichmentJob
from app.schemas.webhook import ClayWebhookPayload
from app.services.enrichment_service import EnrichmentService
from backend.app.services.clay_service import ClayWebhookService

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post(
    "/trigger",
    status_code=status.HTTP_202_ACCEPTED,
)
async def trigger_enrichment(
    email: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Initiate Clay enrichment for a given email address.
    
    This endpoint:
    1. Creates a new enrichment job record in the database
    2. Builds callback URL using PUBLIC_BASE_URL
    3. Sends POST request to Clay webhook URL with email, job_id, and callback_url
    4. Returns immediately while Clay processes the enrichment asynchronously
    
    Args:
        email: Email address to enrich
        background_tasks: FastAPI background tasks for async processing
        db: Async database session
    
    Returns:
        dict: Success response with job_id and status
    
    Raises:
        HTTPException: If job creation or Clay request fails
    """
    try:
        # Initialize service
        service = EnrichmentService(db)
        
        # Create new enrichment job using service
        job = await service.create_job(email=email)
        
        logger.info(f"Created enrichment job {job.job_id} for email {email}")
        
        # Initialize Clay webhook service
        clay_service = ClayWebhookService()
        
        # Send enrichment request to Clay in background
        # Note: Background tasks are executed after the response is sent
        # The actual HTTP call to Clay will happen in the background
        background_tasks.add_task(
            clay_service.trigger_enrichment,
            email=email,
            job_id=job.job_id,
        )
        
        return {
            "status": ResponseStatus.ACCEPTED,
            "job_id": str(job.job_id),
            "email": email,
            "message": "Enrichment request accepted and sent to Clay",
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions
        raise
    except Exception as e:
        logger.error(f"Failed to create enrichment job for email {email}: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate enrichment: {str(e)}",
        )


@router.post(
    "/clay",
    status_code=status.HTTP_200_OK,
)
async def receive_clay_webhook_callback(
    payload: ClayWebhookPayload,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Receive Clay webhook callback with payload and update enrichment job.
    
    This endpoint handles direct POST requests with ClayWebhookPayload in body
    from Clay's webhook system.
    
    Args:
        payload: Clay webhook payload with job data.
        db: Async database session.
    
    Returns:
        dict: Success response with job_id and updated payload_type.
    
    Raises:
        HTTPException: If job is not found or update fails.
    """
    try:
        service = EnrichmentService(db)
        
        # Handle direct POST with payload in body
        logger.info(f"Processing Clay webhook for job {payload.job_id}, payload_type: {payload.payload_type}")
        job = await service.handle_clay_callback(payload)
        updated_payload_type = payload.payload_type
        
        logger.info(f"Successfully processed webhook for job {job.job_id}, updated payload: {updated_payload_type}")
        
        return {
            "status": "success",
            "job_id": str(job.job_id),
            "updated_payload": updated_payload_type,
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions (e.g., 404 Not Found)
        raise
    except Exception as e:
        logger.error(f"Failed to process webhook: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}",
        )


@router.post(
    "/clay/trigger/{job_id}",
    status_code=status.HTTP_200_OK,
)
async def trigger_clay_webhook_from_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Trigger a Clay webhook callback for a specific job using job_id.
    
    This is a diagnostic/fallback endpoint that creates a minimal synthetic payload
    and processes it as if it came from Clay. Useful for testing or manual reprocessing.
    
    Args:
        job_id: Job identifier from URL path.
        db: Async database session.
    
    Returns:
        dict: Success response with job_id and updated payload_type.
    
    Raises:
        HTTPException: If job is not found or update fails.
    """
    try:
        service = EnrichmentService(db)
        
        # Fetch the job from database to get the email
        result = await db.execute(
            select(EnrichmentJob).where(EnrichmentJob.job_id == UUID(job_id))
        )
        job_record = result.scalar_one_or_none()
        
        if not job_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found",
            )
        
        # Create a minimal payload with the email from the database
        query_payload = ClayWebhookPayload(
            job_id=job_id,
            email=job_record.email,
            payload_type="person",  # Default type for diagnostic case
            data={},  # Empty data for diagnostic reprocessing
        )
        
        logger.info(f"Triggering diagnostic webhook for job {job_id}")
        job = await service.handle_clay_callback(query_payload)
        
        logger.info(f"Successfully processed diagnostic webhook for job {job.job_id}")
        
        return {
            "status": "success",
            "job_id": str(job.job_id),
            "updated_payload": "diagnostic",
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions (e.g., 404 Not Found)
        raise
    except Exception as e:
        logger.error(f"Failed to trigger diagnostic webhook: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger diagnostic webhook: {str(e)}",
        )



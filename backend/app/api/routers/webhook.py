"""Webhook router for receiving Clay webhook data."""
import logging
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.enrichment import EnrichmentJob
from app.schemas.enrichment import (
    EnrichmentJobCreate,
    EnrichmentJobResponse,
    EnrichmentJobUpdate,
)
from app.schemas.webhook import ClayWebhookPayload
from app.schemas.enriched_data import LeadProfileView
from app.services.enrichment_service import EnrichmentService
from app.services.clay_webhook_service import ClayWebhookService

from typing import Optional

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
        # Create new enrichment job
        job_id = uuid4()
        job = EnrichmentJob(
            id=uuid4(),
            job_id=job_id,
            email=email,
            status="pending",
        )
        
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        logger.info(f"Created enrichment job {job_id} for email {email}")
        
        # Initialize Clay webhook service
        clay_service = ClayWebhookService()
        
        # Send enrichment request to Clay in background
        # Note: Background tasks are executed after the response is sent
        # The actual HTTP call to Clay will happen in the background
        background_tasks.add_task(
            clay_service.trigger_enrichment,
            email=email,
            job_id=job_id,
        )
        
        return {
            "status": "accepted",
            "job_id": str(job_id),
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
async def receive_clay_webhook(
    payload: ClayWebhookPayload = None,
    job_id: str = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Receive Clay webhook callback and update enrichment job.
    
    This endpoint handles both:
    1. Direct POST requests with ClayWebhookPayload in body
    2. Query parameter requests with job_id in URL
    
    Args:
        payload: Clay webhook payload with job data (optional).
        job_id: Job identifier from query parameters (optional).
        db: Async database session.
    
    Returns:
        dict: Success response with job_id and updated payload_type.
    
    Raises:
        HTTPException: If job is not found or update fails.
    """
    try:
        service = EnrichmentService(db)
        
        # Handle query parameter case
        if job_id and not payload:
            # When job_id is provided via query parameter but no payload in body
            # We need to fetch the job from database to get the email
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
                payload_type="person",  # Default type for query param case
                data={},  # Empty data for now
            )
            job = await service.handle_clay_callback(query_payload)
            updated_payload_type = "query_param"
        elif payload:
            # Handle direct POST with payload in body
            logger.info(f"Processing Clay webhook for job {payload.job_id}, payload_type: {payload.payload_type}")
            job = await service.handle_clay_callback(payload)
            updated_payload_type = payload.payload_type
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either payload in body or job_id query parameter is required",
            )
        
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


@router.get(
    "/jobs/{job_id}",
    response_model=EnrichmentJobResponse,
)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> EnrichmentJob:
    """
    Retrieve a specific enrichment job by ID.
    
    Args:
        job_id: UUID of the job to retrieve.
        db: Async database session.
    
    Returns:
        EnrichmentJob: The requested job record.
    
    Raises:
        HTTPException: If job is not found.
    """
    result = await db.execute(
        select(EnrichmentJob).where(EnrichmentJob.job_id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with Clay job ID {job_id} not found",
        )
    
    return job


@router.put(
    "/jobs/{job_id}",
    response_model=EnrichmentJobResponse,
)
async def update_job(
    job_id: UUID,
    update_data: EnrichmentJobUpdate,
    db: AsyncSession = Depends(get_db),
) -> EnrichmentJob:
    """
    Update an existing enrichment job.
    
    Args:
        job_id: UUID of the job to update.
        update_data: Fields to update.
        db: Async database session.
    
    Returns:
        EnrichmentJob: The updated job record.
    
    Raises:
        HTTPException: If job is not found or update fails.
    """
    result = await db.execute(
        select(EnrichmentJob).where(EnrichmentJob.job_id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with Clay job ID {job_id} not found",
        )
    
    # Update fields
    if update_data.status is not None:
        job.status = update_data.status
    if update_data.payload_1 is not None:
        job.payload_1 = update_data.payload_1
    if update_data.payload_2 is not None:
        job.payload_2 = update_data.payload_2
    if update_data.payload_3 is not None:
        job.payload_3 = update_data.payload_3
    if update_data.payload_4 is not None:
        job.payload_4 = update_data.payload_4
    if update_data.payload_5 is not None:
        job.payload_5 = update_data.payload_5
    if update_data.payload_6 is not None:
        job.payload_6 = update_data.payload_6
    
    try:
        await db.commit()
        await db.refresh(job)
        return job
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job: {str(e)}",
        )


@router.delete(
    "/jobs/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete an enrichment job.
    
    Args:
        job_id: UUID of the job to delete.
        db: Async database session.
    
    Raises:
        HTTPException: If job is not found or deletion fails.
    """
    result = await db.execute(
        select(EnrichmentJob).where(EnrichmentJob.job_id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with Clay job ID {job_id} not found",
        )
    
    try:
        await db.delete(job)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job: {str(e)}",
        )


@router.get(
    "/jobs/{job_id}/profile",
    response_model=LeadProfileView,
    summary="Get structured lead profile",
    description="Retrieve fully transformed lead profile with all enriched data combined.",
)
async def get_lead_profile(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> LeadProfileView:
    """
    Retrieve structured lead profile data for a completed enrichment job.
    
    Returns a fully transformed LeadProfileView with all 6 payloads combined.
    """
    # Query the job by job_id (Clay job ID), not the primary key id
    result = await db.execute(
        select(EnrichmentJob).where(EnrichmentJob.job_id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        logger.warning(f"Profile not found for job_id {job_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrichment job with Clay job ID {job_id} not found",
        )
    
    logger.info(f"Building profile for job {job_id}")
    
    # Use the static method from EnrichmentService
    return await EnrichmentService.build_profile_from_job(job)

"""Enrichment API router for frontend data fetching."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.enrichment import EnrichmentJob
from app.schemas.enrichment import (
    EnrichmentJobResponse,
    EnrichmentJobUpdate,
    JobSummary,
    ConsolidatedPayload,
)
from app.schemas.enriched_data import LeadProfileView
from app.services.enrichment_service import EnrichmentService

router = APIRouter(prefix="/api/enrichment", tags=["enrichment"])


@router.get(
    "/completed",
    response_model=List[JobSummary],
    status_code=status.HTTP_200_OK,
    summary="Get completed enrichment jobs",
    description="Retrieve all completed enrichment jobs for frontend dropdown selection.",
)
async def get_completed_enrichment_jobs(
    db: AsyncSession = Depends(get_db)
) -> List[JobSummary]:
    """Get all completed enrichment jobs.
    
    Returns:
        List[JobSummary]: List of job summaries for completed jobs.
    """
    try:
        service = EnrichmentService(db)
        return await service.get_completed_jobs()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch completed jobs: {str(e)}",
        )


@router.get(
    "/{job_id}/payload",
    response_model=ConsolidatedPayload,
    status_code=status.HTTP_200_OK,
    summary="Get consolidated payload for a job",
    description="Retrieve a single enrichment job with all its JSONB payloads.",
)
async def get_job_payload(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> ConsolidatedPayload:
    """Get a single job with all its JSONB payloads.
    
    Args:
        job_id: The job identifier (UUID string).
        db: Async database session.
    
    Returns:
        ConsolidatedPayload: The job with all payload data.
    
    Raises:
        HTTPException: If job is not found or invalid ID format.
    """
    try:
        service = EnrichmentService(db)
        return await service.get_consolidated_payload(job_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch job payload: {str(e)}",
        )


@router.get(
    "/{job_id}/profile",
    response_model=LeadProfileView,
    status_code=status.HTTP_200_OK,
    summary="Get transformed lead profile for a job",
    description="Retrieve a single enrichment job with transformed, clean profile data.",
)
async def get_lead_profile_endpoint(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> LeadProfileView:
    """Get a single job with transformed, clean profile data.
    
    This endpoint returns the transformed LeadProfileView instead of raw payloads.
    The data is processed through transformers to create a structured, clean view.
    
    Args:
        job_id: The job identifier (UUID string).
        db: Async database session.
    
    Returns:
        LeadProfileView: Transformed and validated lead profile data.
    
    Raises:
        HTTPException: If job is not found or invalid ID format.
    """
    try:
        service = EnrichmentService(db)
        return await service.get_lead_profile(job_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch lead profile: {str(e)}",
        )


@router.get(
    "/jobs/{job_id}",
    response_model=EnrichmentJobResponse,
    status_code=status.HTTP_200_OK,
    summary="Get enrichment job by ID",
    description="Retrieve a specific enrichment job by its UUID.",
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
            detail=f"Job with ID {job_id} not found",
        )
    
    return job


@router.put(
    "/jobs/{job_id}",
    response_model=EnrichmentJobResponse,
    status_code=status.HTTP_200_OK,
    summary="Update enrichment job",
    description="Update an existing enrichment job's fields.",
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
            detail=f"Job with ID {job_id} not found",
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
    summary="Delete enrichment job",
    description="Delete an enrichment job by its UUID.",
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
            detail=f"Job with ID {job_id} not found",
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

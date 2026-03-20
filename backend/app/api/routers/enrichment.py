"""Enrichment API router for frontend data fetching."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.enrichment import JobSummary, ConsolidatedPayload
from app.schemas.enriched_data import LeadProfileView
from app.services.enrichment_service import (
    get_completed_jobs,
    get_consolidated_payload,
    get_lead_profile,
)

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
        return await get_completed_jobs(db)
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
        return await get_consolidated_payload(db, job_id)
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
        return await get_lead_profile(db, job_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch lead profile: {str(e)}",
        )

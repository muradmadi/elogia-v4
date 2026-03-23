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
from app.schemas.enriched_data import (
    PersonSchema, CompanySchema, ProfileSchema,
    ProductSchema, PainPointsSchema, CommunicationSchema
)
from app.schemas.lead_profile import LeadProfileView
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
    response_model=ProfileSchema,
    status_code=status.HTTP_200_OK,
    summary="Get transformed profile data for a job",
    description="Retrieve transformed profile data (payload 3 only) for frontend display.",
)
async def get_profile_endpoint(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> ProfileSchema:
    """Get transformed profile data (payload 3 only).
    
    This endpoint returns the transformed ProfileSchema for the profile card.
    The data is processed through transformers to create a structured, clean view.
    
    Args:
        job_id: The job identifier (UUID string).
        db: Async database session.
    
    Returns:
        ProfileSchema: Transformed and validated profile data.
    
    Raises:
        HTTPException: If job is not found or invalid ID format.
    """
    try:
        service = EnrichmentService(db)
        return await service.get_profile_schema(job_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch profile data: {str(e)}",
        )

@router.get(
    "/{job_id}/lead-profile",
    response_model=LeadProfileView,
    status_code=status.HTTP_200_OK,
    summary="Get consolidated lead profile for a job",
    description="Retrieve a consolidated lead profile view with all 6 payloads stitched together.",
)
async def get_lead_profile_endpoint(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> LeadProfileView:
    """Get a consolidated lead profile view.
    
    This endpoint returns the transformed LeadProfileView (all 6 payloads stitched together).
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
    "/{job_id}/person",
    response_model=PersonSchema,
    status_code=status.HTTP_200_OK,
    summary="Get transformed person data for a job",
    description="Retrieve transformed person data (payload 1) for frontend display.",
)
async def get_person_endpoint(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> PersonSchema:
    """Get transformed person data (payload 1).
    
    Args:
        job_id: The job identifier (UUID string).
        db: Async database session.
    
    Returns:
        PersonSchema: Transformed person data.
    
    Raises:
        HTTPException: If job is not found or payload is missing.
    """
    try:
        service = EnrichmentService(db)
        return await service.get_person_schema(job_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch person data: {str(e)}",
        )

@router.get(
    "/{job_id}/company",
    response_model=CompanySchema,
    status_code=status.HTTP_200_OK,
    summary="Get transformed company data for a job",
    description="Retrieve transformed company data (payload 2) for frontend display.",
)
async def get_company_endpoint(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> CompanySchema:
    """Get transformed company data (payload 2).
    
    Args:
        job_id: The job identifier (UUID string).
        db: Async database session.
    
    Returns:
        CompanySchema: Transformed company data.
    
    Raises:
        HTTPException: If job is not found or payload is missing.
    """
    try:
        service = EnrichmentService(db)
        return await service.get_company_schema(job_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch company data: {str(e)}",
        )

@router.get(
    "/{job_id}/products",
    response_model=List[ProductSchema],
    status_code=status.HTTP_200_OK,
    summary="Get transformed products data for a job",
    description="Retrieve transformed products data (payload 4) for frontend display.",
)
async def get_products_endpoint(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> List[ProductSchema]:
    """Get transformed products data (payload 4).
    
    Args:
        job_id: The job identifier (UUID string).
        db: Async database session.
    
    Returns:
        List[ProductSchema]: List of transformed product data.
    
    Raises:
        HTTPException: If job is not found or payload is missing.
    """
    try:
        service = EnrichmentService(db)
        return await service.get_products_schema(job_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch products data: {str(e)}",
        )

@router.get(
    "/{job_id}/painpoints",
    response_model=PainPointsSchema,
    status_code=status.HTTP_200_OK,
    summary="Get transformed pain points data for a job",
    description="Retrieve transformed pain points data (payload 5) for frontend display.",
)
async def get_painpoints_endpoint(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> PainPointsSchema:
    """Get transformed pain points data (payload 5).
    
    Args:
        job_id: The job identifier (UUID string).
        db: Async database session.
    
    Returns:
        PainPointsSchema: Transformed pain points data.
    
    Raises:
        HTTPException: If job is not found or payload is missing.
    """
    try:
        service = EnrichmentService(db)
        return await service.get_painpoints_schema(job_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pain points data: {str(e)}",
        )

@router.get(
    "/{job_id}/communication",
    response_model=CommunicationSchema,
    status_code=status.HTTP_200_OK,
    summary="Get transformed communication data for a job",
    description="Retrieve transformed communication data (payload 6) for frontend display.",
)
async def get_communication_endpoint(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> CommunicationSchema:
    """Get transformed communication data (payload 6).
    
    Args:
        job_id: The job identifier (UUID string).
        db: Async database session.
    
    Returns:
        CommunicationSchema: Transformed communication data.
    
    Raises:
        HTTPException: If job is not found or payload is missing.
    """
    try:
        service = EnrichmentService(db)
        return await service.get_communication_schema(job_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch communication data: {str(e)}",
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

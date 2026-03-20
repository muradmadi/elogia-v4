"""Service layer for handling enrichment webhook processing."""
from typing import Optional, List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enrichment import EnrichmentJob
from app.models.sequence import CampaignSequence
from app.schemas.enrichment import JobSummary, ConsolidatedPayload
from app.schemas.webhook import ClayWebhookPayload
from app.schemas.enriched_data import LeadProfileView
from app.schemas.sequence import ClaudeOutreachView
from app.transformers.main import build_lead_profile
from app.transformers import validate_claude_outreach


class EnrichmentService:
    """Service for processing Clay webhook callbacks and updating enrichment jobs."""
    
    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session.
        
        Args:
            db: Async database session.
        """
        self.db = db
    
    async def handle_clay_callback(
        self,
        payload: ClayWebhookPayload,
    ) -> EnrichmentJob:
        """Process Clay webhook callback and update enrichment job.
        
        Args:
            payload: Clay webhook payload with job data.
        
        Returns:
            EnrichmentJob: Updated job record.
        
        Raises:
            HTTPException: If job is not found or update fails.
        """
        # Query the enrichment job by job_id
        result = await self.db.execute(
            select(EnrichmentJob).where(
                EnrichmentJob.job_id == UUID(payload.job_id)
            )
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrichment job with ID {payload.job_id} not found",
            )
        
        # Dynamically update the specific JSONB payload column
        # based on the payload_type
        if payload.payload_type == "person":
            job.payload_1 = payload.data
        elif payload.payload_type == "company":
            job.payload_2 = payload.data
        elif payload.payload_type == "profile":
            job.payload_3 = payload.data
        elif payload.payload_type == "products":
            job.payload_4 = payload.data
        elif payload.payload_type == "painpoints":
            job.payload_5 = payload.data
        elif payload.payload_type == "communication":
            job.payload_6 = payload.data
        
        # Check the state of all 6 payload columns
        # If none of them are null anymore, update status to "completed"
        all_payloads_filled = (
            job.payload_1 is not None
            and job.payload_2 is not None
            and job.payload_3 is not None
            and job.payload_4 is not None
            and job.payload_5 is not None
            and job.payload_6 is not None
        )
        
        if all_payloads_filled:
            job.status = "completed"
        
        # Commit the transaction and refresh the object
        try:
            await self.db.commit()
            await self.db.refresh(job)
            return job
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update enrichment job: {str(e)}",
            )
    
    @staticmethod
    async def build_profile_from_job(job: EnrichmentJob) -> LeadProfileView:
        """
        Transform an EnrichmentJob into a structured LeadProfileView.
        
        Args:
            job: The enrichment job with all 6 payloads
            
        Returns:
            LeadProfileView: Structured profile data ready for frontend
        """
        return build_lead_profile(
            person_payload=job.payload_1 or {},
            company_payload=job.payload_2,
            role_intelligence_payload=job.payload_3,
            product_payload=job.payload_4,
            pain_payload=job.payload_5,
            outreach_payload=job.payload_6,
        )


async def get_completed_jobs(db_session: AsyncSession) -> List[JobSummary]:
    """Get all completed enrichment jobs.
    
    Args:
        db_session: Async database session.
    
    Returns:
        List[JobSummary]: List of job summaries for completed jobs.
    """
    result = await db_session.execute(
        select(EnrichmentJob).where(EnrichmentJob.status == "completed")
    )
    jobs = result.scalars().all()
    
    return [
        JobSummary(
            job_id=job.job_id,
            email=job.email,
            status=job.status,
        )
        for job in jobs
    ]


async def get_consolidated_payload(
    db_session: AsyncSession, job_id: str
) -> ConsolidatedPayload:
    """Get a single job with all its JSONB payloads.
    
    Args:
        db_session: Async database session.
        job_id: The job identifier (UUID string).
    
    Returns:
        ConsolidatedPayload: The job with all payload data.
    
    Raises:
        HTTPException: If job is not found.
    """
    try:
        uuid_job_id = UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid job ID format: {job_id}",
        )
    
    result = await db_session.execute(
        select(EnrichmentJob).where(EnrichmentJob.job_id == uuid_job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrichment job with ID {job_id} not found",
        )
    
    return ConsolidatedPayload(
        id=job.id,
        job_id=job.job_id,
        email=job.email,
        status=job.status,
        payload_1=job.payload_1,
        payload_2=job.payload_2,
        payload_3=job.payload_3,
        payload_4=job.payload_4,
        payload_5=job.payload_5,
        payload_6=job.payload_6,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


async def get_lead_profile(
    db_session: AsyncSession, job_id: str
) -> LeadProfileView:
    """Get transformed lead profile for a job.
    
    Args:
        db_session: Async database session.
        job_id: The job identifier (UUID string).
    
    Returns:
        LeadProfileView: Transformed and validated lead profile data.
    
    Raises:
        HTTPException: If job is not found.
    """
    try:
        uuid_job_id = UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid job ID format: {job_id}",
        )
    
    result = await db_session.execute(
        select(EnrichmentJob).where(EnrichmentJob.job_id == uuid_job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrichment job with ID {job_id} not found",
        )
    
    # Transform raw payloads into structured LeadProfileView
    return await EnrichmentService.build_profile_from_job(job)


async def get_sequence_data(
    db_session: AsyncSession, job_id: str
) -> ClaudeOutreachView:
    """Get validated sequence data for a job.
    
    Args:
        db_session: Async database session.
        job_id: The job identifier (UUID string).
    
    Returns:
        ClaudeOutreachView: Validated sequence data from Claude.
    
    Raises:
        HTTPException: If job or sequence is not found.
    """
    try:
        uuid_job_id = UUID(job_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid job ID format: {job_id}",
        )
    
    # Get the sequence for this job
    result = await db_session.execute(
        select(CampaignSequence).where(
            CampaignSequence.enrichment_job_id == uuid_job_id
        )
    )
    sequence = result.scalar_one_or_none()
    
    if not sequence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sequence for job {job_id} not found",
        )
    
    if not sequence.sequence_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sequence data not yet generated for job {job_id}",
        )
    
    # Validate and return the sequence data
    return validate_claude_outreach(sequence.sequence_data)

"""Service layer for handling sequence operations."""
import logging
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.status import CampaignSequenceStatus
from app.models.enrichment import EnrichmentJob
from app.models.sequence import CampaignSequence
from app.schemas.sequence import ClaudeOutreachView
from app.transformers.sequence import validate_claude_response

logger = logging.getLogger(__name__)


class SequenceService:
    """Service for handling sequence operations including creation and retrieval."""
    
    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session.
        
        Args:
            db: Async database session.
        """
        self.db = db
    
    async def get_or_create_sequence(
        self,
        job_id: UUID,
    ) -> CampaignSequence:
        """Get an existing sequence for a job or create a new one.
        
        This method checks if a sequence already exists for the given job.
        If it exists, returns it. If not, creates a new sequence record.
        
        Args:
            job_id: The enrichment job ID (UUID).
            
        Returns:
            CampaignSequence: The existing or newly created sequence record.
            
        Raises:
            HTTPException: If the job is not found or sequence creation fails.
        """
        try:
            # Check if the job exists in the database
            result = await self.db.execute(
                select(EnrichmentJob).where(EnrichmentJob.job_id == job_id)
            )
            job = result.scalar_one_or_none()
            
            if not job:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Enrichment job with ID {job_id} not found",
                )
            
            # Check if a sequence already exists for this job
            result = await self.db.execute(
                select(CampaignSequence).where(
                    CampaignSequence.enrichment_job_id == job_id
                )
            )
            existing_sequence = result.scalar_one_or_none()
            
            if existing_sequence:
                return existing_sequence
            
            # Create a new sequence record
            new_sequence = CampaignSequence(
                enrichment_job_id=job_id,
                status=CampaignSequenceStatus.GENERATING,
            )
            self.db.add(new_sequence)
            await self.db.commit()
            await self.db.refresh(new_sequence)
            
            return new_sequence
            
        except HTTPException:
            # Re-raise HTTPExceptions
            raise
        except Exception as e:
            logger.error(f"Failed to get or create sequence for job {job_id}: {str(e)}", exc_info=True)
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get or create sequence: {str(e)}",
            )
    
    async def get_sequence_data(
        self,
        job_id: str,
    ) -> ClaudeOutreachView:
        """Get validated sequence data for a job.
        
        Args:
            job_id: The job identifier (UUID string).
            
        Returns:
            ClaudeOutreachView: Validated sequence data with touches and strategy.
            
        Raises:
            HTTPException: If job or sequence is not found, or data not yet generated.
        """
        try:
            # Validate job_id format
            try:
                uuid_job_id = UUID(job_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid job ID format: {job_id}",
                )
            
            # Get the sequence for this job
            result = await self.db.execute(
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
            return validate_claude_response(sequence.sequence_data)
            
        except HTTPException:
            # Re-raise HTTPExceptions
            raise
        except Exception as e:
            logger.error(f"Failed to fetch sequence data for job {job_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch sequence data: {str(e)}",
            )

"""Service for generating email sequences using LLM."""
import json
import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.prompts import MASTER_SYSTEM_PROMPT
from app.models.enrichment import EnrichmentJob
from app.models.sequence import CampaignSequence
from app.services.enrichment_service import EnrichmentService
from app.services.llm_service import llm_service
from app.transformers import validate_claude_outreach

logger = logging.getLogger(__name__)


async def generate_sequence(
    db_session: AsyncSession,
    job_id: str,
) -> CampaignSequence:
    """Generate an 8-touch email sequence for a job.
    
    Logic flow:
    1. Check if a CampaignSequence already exists for this job_id
    2. If not, create one with status="generating"
    3. If it does exist, update status to "generating"
    4. Commit the session so the frontend sees the status change immediately
    5. Fetch the consolidated payload
    6. Stringify the massive JSON payload to pass into the LLM context
    7. Call the AsyncAnthropic client
    8. Parse the response with robust string stripping
    9. Save the parsed JSON into the sequence_data column
    10. Save the MASTER_SYSTEM_PROMPT into the master_prompt_used column
    11. Update status to "completed" and commit
    
    Args:
        db_session: Async database session.
        job_id: The enrichment job ID (UUID string).
    
    Returns:
        CampaignSequence: The generated or updated sequence record.
    
    Raises:
        Exception: If any step fails, the sequence status is set to 'failed'.
    """
    try:
        # Step 1: Check if a CampaignSequence already exists for this job_id
        uuid_job_id = UUID(job_id)
        result = await db_session.execute(
            select(CampaignSequence).where(
                CampaignSequence.enrichment_job_id == uuid_job_id
            )
        )
        sequence = result.scalar_one_or_none()
        
        # Step 2 & 3: Create or update the sequence with status="generating"
        if sequence is None:
            # Create a new sequence
            sequence = CampaignSequence(
                enrichment_job_id=uuid_job_id,
                status="generating",
            )
            db_session.add(sequence)
        else:
            # Update existing sequence status
            sequence.status = "generating"
        
        # Step 4: Commit the session so the frontend sees the status change immediately
        await db_session.commit()
        await db_session.refresh(sequence)
        
        # Step 5: Fetch the consolidated payload
        result = await db_session.execute(
            select(EnrichmentJob).where(EnrichmentJob.job_id == uuid_job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise ValueError(f"Enrichment job with ID {job_id} not found")
        
        # Step 7: Call the AsyncAnthropic client with TRANSFORMED data
        try:
            # Transform all 6 payloads into structured LeadProfileView
            lead_profile = await EnrichmentService.build_profile_from_job(job)
            
            # Send transformed data to Claude
            raw_response = await llm_service.generate_sequence(lead_profile.model_dump())
            
            # Step 8: Validate and transform Claude's response into structured data
            validated_sequence = validate_claude_outreach(raw_response)
            
            # Step 9: Save the validated sequence data into the sequence_data column
            sequence.sequence_data = validated_sequence.model_dump()
        except Exception as e:
            logger.error(f"LLM generation failed for job {job_id}: {e}")
            # Update status to 'failed' and commit
            sequence.status = "failed"
            await db_session.commit()
            raise
        
        # Step 10: Save the MASTER_SYSTEM_PROMPT into the master_prompt_used column
        sequence.master_prompt_used = MASTER_SYSTEM_PROMPT
        
        # Step 11: Update status to "completed" and commit
        sequence.status = "completed"
        await db_session.commit()
        await db_session.refresh(sequence)
        
        logger.info(f"Successfully generated sequence for job {job_id}")
        return sequence
        
    except Exception as e:
        logger.error(f"Failed to generate sequence for job {job_id}: {e}")
        
        # Try to update the sequence status to 'failed' if it exists
        try:
            if 'sequence' in locals() and sequence is not None:
                sequence.status = "failed"
                await db_session.commit()
        except Exception as commit_error:
            logger.error(f"Failed to update sequence status to failed: {commit_error}")
        
        raise

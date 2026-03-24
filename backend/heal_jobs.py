import asyncio
import logging
from sqlalchemy import select
from app.core.database import async_sessionmaker, engine
from app.models.enrichment import EnrichmentJob
from app.core.status import EnrichmentJobStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def heal_stuck_jobs():
    """Finds jobs that are stuck in 'pending' but have all 6 payloads and marks them as 'completed'."""
    logger.info("Connecting to the database...")
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        # Query all pending jobs
        logger.info("Querying for pending enrichment jobs...")
        result = await session.execute(
            select(EnrichmentJob).where(EnrichmentJob.status == EnrichmentJobStatus.PENDING)
        )
        jobs = result.scalars().all()
        
        fixed_count = 0
        
        for job in jobs:
            # Check if all payloads are filled
            all_payloads_filled = (
                job.payload_1 is not None
                and job.payload_2 is not None
                and job.payload_3 is not None
                and job.payload_4 is not None
                and job.payload_5 is not None
                and job.payload_6 is not None
            )
            
            if all_payloads_filled:
                logger.info(f"Healing job {job.job_id} for email {job.email} - marking as completed.")
                job.status = EnrichmentJobStatus.COMPLETED
                fixed_count += 1
        
        if fixed_count > 0:
            logger.info(f"Committing {fixed_count} fixed jobs to the database...")
            await session.commit()
            logger.info("Healing complete!")
        else:
            logger.info("No stuck jobs found to heal.")

if __name__ == "__main__":
    asyncio.run(heal_stuck_jobs())

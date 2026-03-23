"""Service layer for handling enrichment webhook processing."""
from typing import Optional, List, Dict
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.status import EnrichmentJobStatus
from app.models.enrichment import EnrichmentJob
from app.schemas.enrichment import JobSummary, ConsolidatedPayload
from app.schemas.webhook import ClayWebhookPayload
from app.schemas.enriched_data import (
    PersonSchema, CompanySchema, ProfileSchema,
    ProductSchema, PainPointsSchema, CommunicationSchema
)
from app.schemas.lead_profile import LeadProfileView
from app.transformers import build_lead_profile


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
                EnrichmentJob.job_id == payload.job_id
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
            job.status = EnrichmentJobStatus.COMPLETED
        
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
    
    async def create_job(
        self,
        email: str,
    ) -> EnrichmentJob:
        """Create a new enrichment job.
        
        Args:
            email: Email address to enrich.
            
        Returns:
            EnrichmentJob: The newly created job record.
            
        Raises:
            HTTPException: If job creation fails.
        """
        try:
            # Create new enrichment job
            job_id = uuid4()
            job = EnrichmentJob(
                job_id=job_id,
                email=email,
                status=EnrichmentJobStatus.PENDING,
            )
            
            self.db.add(job)
            await self.db.commit()
            await self.db.refresh(job)
            
            return job
            
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create enrichment job: {str(e)}",
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
    
    async def get_completed_jobs(self) -> List[JobSummary]:
        """Get all completed enrichment jobs.
        
        Returns:
            List[JobSummary]: List of job summaries for completed jobs.
        """
        result = await self.db.execute(
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
        self,
        job_id: str,
    ) -> ConsolidatedPayload:
        """Get a single job with all its JSONB payloads.
        
        Args:
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
        
        result = await self.db.execute(
            select(EnrichmentJob).where(EnrichmentJob.job_id == uuid_job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrichment job with ID {job_id} not found",
            )
        
        return ConsolidatedPayload(
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
        self,
        job_id: str,
    ) -> LeadProfileView:
        """Get transformed lead profile for a job.
        
        Args:
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
        
        result = await self.db.execute(
            select(EnrichmentJob).where(EnrichmentJob.job_id == uuid_job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrichment job with ID {job_id} not found",
            )
        
        # Transform raw payloads into structured LeadProfileView
        return await self.build_profile_from_job(job)

    async def get_person_schema(
        self,
        job_id: str,
    ) -> PersonSchema:
        """Get transformed person data (payload 1).
        
        Args:
            job_id: The job identifier (UUID string).
        
        Returns:
            PersonSchema: Transformed person data.
        
        Raises:
            HTTPException: If job is not found or payload is missing.
        """
        try:
            uuid_job_id = UUID(job_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid job ID format: {job_id}",
            )
        
        result = await self.db.execute(
            select(EnrichmentJob).where(EnrichmentJob.job_id == uuid_job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrichment job with ID {job_id} not found",
            )
        
        if not job.payload_1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person payload not yet available for job {job_id}",
            )
        
        # Transform using person transformer
        from app.transformers.person import transform_person
        person_data = transform_person(job.payload_1)
        return PersonSchema.model_validate(person_data)

    async def get_company_schema(
        self,
        job_id: str,
    ) -> CompanySchema:
        """Get transformed company data (payload 2).
        
        Args:
            job_id: The job identifier (UUID string).
        
        Returns:
            CompanySchema: Transformed company data.
        
        Raises:
            HTTPException: If job is not found or payload is missing.
        """
        try:
            uuid_job_id = UUID(job_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid job ID format: {job_id}",
            )
        
        result = await self.db.execute(
            select(EnrichmentJob).where(EnrichmentJob.job_id == uuid_job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrichment job with ID {job_id} not found",
            )
        
        if not job.payload_2:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company payload not yet available for job {job_id}",
            )
        
        # Transform using company transformer
        from app.transformers.company import transform_company
        company_data = transform_company(job.payload_2)
        return CompanySchema.model_validate(company_data)

    async def get_profile_schema(
        self,
        job_id: str,
    ) -> ProfileSchema:
        """Get transformed profile data (payload 3 only).
        
        Args:
            job_id: The job identifier (UUID string).
        
        Returns:
            ProfileSchema: Transformed profile data.
        
        Raises:
            HTTPException: If job is not found or payload is missing.
        """
        try:
            uuid_job_id = UUID(job_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid job ID format: {job_id}",
            )
        
        result = await self.db.execute(
            select(EnrichmentJob).where(EnrichmentJob.job_id == uuid_job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrichment job with ID {job_id} not found",
            )
        
        if not job.payload_3:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile payload not yet available for job {job_id}",
            )
        
        # Transform using profile transformer
        from app.transformers.profile import transform_profile
        profile_data = transform_profile(job.payload_3)
        return ProfileSchema.model_validate(profile_data)

    async def get_products_schema(
        self,
        job_id: str,
    ) -> List[ProductSchema]:
        """Get transformed products data (payload 4).
        
        Args:
            job_id: The job identifier (UUID string).
        
        Returns:
            List[ProductSchema]: List of transformed product data.
        
        Raises:
            HTTPException: If job is not found or payload is missing.
        """
        try:
            uuid_job_id = UUID(job_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid job ID format: {job_id}",
            )
        
        result = await self.db.execute(
            select(EnrichmentJob).where(EnrichmentJob.job_id == uuid_job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrichment job with ID {job_id} not found",
            )
        
        if not job.payload_4:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Products payload not yet available for job {job_id}",
            )
        
        # Transform using product transformer
        from app.transformers.products import transform_product
        product_data = transform_product(job.payload_4)
        # Return as list to match frontend expectation
        return [ProductSchema.model_validate(product_data)]

    async def get_painpoints_schema(
        self,
        job_id: str,
    ) -> PainPointsSchema:
        """Get transformed pain points data (payload 5).
        
        Args:
            job_id: The job identifier (UUID string).
        
        Returns:
            PainPointsSchema: Transformed pain points data.
        
        Raises:
            HTTPException: If job is not found or payload is missing.
        """
        try:
            uuid_job_id = UUID(job_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid job ID format: {job_id}",
            )
        
        result = await self.db.execute(
            select(EnrichmentJob).where(EnrichmentJob.job_id == uuid_job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrichment job with ID {job_id} not found",
            )
        
        if not job.payload_5:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pain points payload not yet available for job {job_id}",
            )
        
        # Transform using pain points transformer
        from app.transformers.intelligence import transform_pain_points
        pain_data = transform_pain_points(job.payload_5)
        if not pain_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pain points transformation failed for job {job_id}",
            )
        
        # Convert to PainPointsSchema format
        from app.schemas.enriched_data import PainPointsSchema, TopPainsSummaryView, PainPointDetailView
        from typing import Dict
        
        # Convert categories from list to dict
        categories_dict: Dict[str, List[PainPointDetailView]] = {}
        for category in pain_data.get("categories", []):
            category_name = category.get("name", "uncategorized")
            pain_points = []
            for pain in category.get("pain_points", []):
                pain_points.append(PainPointDetailView(
                    pain_point=pain.get("pain_point", ""),
                    description=pain.get("description", ""),
                    urgency=pain.get("urgency", ""),
                    frequency=pain.get("frequency", ""),
                    impact=pain.get("impact", ""),
                    evidence=pain.get("evidence", ""),
                    evidence_level=pain.get("evidence_level", "")
                ))
            categories_dict[category_name] = pain_points
        
        # Create top pains summary
        top_pains_data = pain_data.get("top_pains", {})
        top_pains = TopPainsSummaryView(
            most_urgent=top_pains_data.get("most_urgent", ""),
            most_frequent=top_pains_data.get("most_frequent", ""),
            most_impactful=top_pains_data.get("most_impactful", "")
        )
        
        return PainPointsSchema(
            notes=pain_data.get("notes"),
            role_scope=pain_data.get("subject_title"),
            top_pains=top_pains,
            categories=categories_dict
        )

    async def get_communication_schema(
        self,
        job_id: str,
    ) -> CommunicationSchema:
        """Get transformed communication data (payload 6).
        
        Args:
            job_id: The job identifier (UUID string).
        
        Returns:
            CommunicationSchema: Transformed communication data.
        
        Raises:
            HTTPException: If job is not found or payload is missing.
        """
        try:
            uuid_job_id = UUID(job_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid job ID format: {job_id}",
            )
        
        result = await self.db.execute(
            select(EnrichmentJob).where(EnrichmentJob.job_id == uuid_job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrichment job with ID {job_id} not found",
            )
        
        if not job.payload_6:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Communication payload not yet available for job {job_id}",
            )
        
        # Transform using outreach strategy transformer
        from app.transformers.intelligence import transform_outreach_strategy
        outreach_data = transform_outreach_strategy(job.payload_6)
        if not outreach_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Communication transformation failed for job {job_id}",
            )
        
        # Convert to CommunicationSchema format
        from app.schemas.enriched_data import (
            CommunicationSchema, StrategicPositioningView, MessageArchitectureView,
            ChannelStrategyView, ChannelFormatView, ChannelTimingView,
            AngleVariantView, RiskMitigationView, PainSolutionMapView,
            ArchitectureElementView
        )
        
        # Convert message architecture
        message_arch_data = outreach_data.get("message_architecture", {})
        message_architecture = MessageArchitectureView(
            hook=ArchitectureElementView(
                text=message_arch_data.get("hook", ""),
                source=None,
                rationale=None
            ),
            bridge=ArchitectureElementView(
                text=message_arch_data.get("bridge", ""),
                source=None,
                rationale=None
            ),
            proof=ArchitectureElementView(
                text=message_arch_data.get("proof", ""),
                source=None,
                rationale=None
            ),
            ask=ArchitectureElementView(
                text=message_arch_data.get("ask", ""),
                source=None,
                rationale=None
            )
        )
        
        # Convert channel strategy
        channel_strat_data = outreach_data.get("channel_strategy", {})
        timing_data = channel_strat_data.get("timing", {})
        format_data = channel_strat_data.get("format", {})
        
        channel_strategy = ChannelStrategyView(
            primary_channel=channel_strat_data.get("primary_channel", ""),
            secondary_channel=channel_strat_data.get("secondary_channel", ""),
            format=ChannelFormatView(
                style=format_data.get("style", ""),
                length=format_data.get("length", ""),
                reasoning=format_data.get("reasoning")
            ),
            timing=ChannelTimingView(
                best_time=timing_data.get("best_time", ""),
                avoid_time=timing_data.get("avoid_time", ""),
                reasoning=timing_data.get("reasoning")
            )
        )
        
        # Convert angle variants
        angle_variants = []
        for angle in outreach_data.get("angle_variants", []):
            angle_variants.append(AngleVariantView(
                angle_name=angle.get("angle_name", ""),
                target_pain=angle.get("target_pain", ""),
                opening=angle.get("opening", ""),
                framing=angle.get("framing", ""),
                proof_point=angle.get("proof_point", ""),
                cta=angle.get("cta", "")
            ))
        
        # Convert risk mitigation
        risk_mitigation = []
        for risk in outreach_data.get("risk_mitigation", []):
            risk_mitigation.append(RiskMitigationView(
                risk=risk.get("risk", ""),
                impact=risk.get("impact", ""),
                likelihood=risk.get("likelihood", ""),
                mitigation=risk.get("mitigation", "")
            ))
        
        # Convert strategic positioning
        strategic_pos_data = outreach_data.get("strategic_positioning", {})
        pain_solution_map = []
        for map_item in strategic_pos_data.get("pain_solution_map", []):
            pain_solution_map.append(PainSolutionMapView(
                their_pain=map_item.get("their_pain", ""),
                your_solution=map_item.get("your_solution", ""),
                evidence_level=map_item.get("evidence_level", ""),
                connection_logic=map_item.get("connection_logic", "")
            ))
        
        strategic_positioning = StrategicPositioningView(
            core_thesis=strategic_pos_data.get("core_thesis", ""),
            pain_solution_map=pain_solution_map
        )
        
        return CommunicationSchema(
            notes=outreach_data.get("notes"),
            strategic_positioning=strategic_positioning,
            message_architecture=message_architecture,
            channel_strategy=channel_strategy,
            angle_variants=angle_variants,
            risk_mitigation=risk_mitigation
        )



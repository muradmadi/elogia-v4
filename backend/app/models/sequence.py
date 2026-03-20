"""CampaignSequence model for storing email sequence data."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, func, ForeignKey, UUID as SQLAlchemyUUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enrichment import EnrichmentJob


class CampaignSequence(Base):
    """Model for storing email sequence data generated from enrichment jobs."""
    
    __tablename__ = "campaign_sequences"
    
    # Primary key - UUID
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        server_default=func.uuid_generate_v4(),
    )
    
    # Foreign key to EnrichmentJob using job_id (not the primary key id)
    enrichment_job_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID,
        ForeignKey("enrichment_jobs.job_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One sequence per job
        index=True,
    )
    
    # Relationship to EnrichmentJob
    enrichment_job: Mapped[EnrichmentJob] = relationship(
        "EnrichmentJob",
        back_populates="campaign_sequences",
        lazy="selectin",  # Async-compatible loading strategy
    )
    
    # Master prompt used for generation (for auditing)
    master_prompt_used: Mapped[Optional[str]] = mapped_column(
        String,  # Text field for large prompts
        nullable=True,
    )
    
    # Structured 8-touch email sequence data
    sequence_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
    )
    
    # Sequence generation status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        server_default="pending",
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
    )
    
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<CampaignSequence(id={self.id}, job_id={self.enrichment_job_id}, status={self.status})>"

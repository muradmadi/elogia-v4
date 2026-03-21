"""EnrichmentJob model for storing webhook data in PostgreSQL JSONB columns."""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, func, UUID as SQLAlchemyUUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.status import EnrichmentJobStatus


class EnrichmentJob(Base):
    """Model for storing enrichment job data with JSONB payload columns."""
    
    __tablename__ = "enrichment_jobs"
    
    # Primary key - job_id (Clay job identifier)
    job_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        server_default=func.uuid_generate_v4(),
    )
    
    # Email being enriched
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    
    # Job status
    status: Mapped[EnrichmentJobStatus] = mapped_column(
        String(50),
        nullable=False,
        default=EnrichmentJobStatus.PENDING,
        server_default=EnrichmentJobStatus.PENDING,
    )
    
    # 6 JSONB payload columns for webhook data
    payload_1: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
    )
    
    payload_2: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
    )
    
    payload_3: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
    )
    
    payload_4: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
    )
    
    payload_5: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
    )
    
    payload_6: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    
    # Relationship to CampaignSequence
    campaign_sequences: Mapped[list["CampaignSequence"]] = relationship(
        "CampaignSequence",
        back_populates="enrichment_job",
        lazy="selectin",  # Async-compatible loading strategy
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<EnrichmentJob(job_id={self.job_id}, email={self.email}, status={self.status})>"

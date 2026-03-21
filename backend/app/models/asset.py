"""MarketingAsset model for storing PDF assets with JSONB webhook data."""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, func, UUID as SQLAlchemyUUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.status import AssetStatus


class MarketingAsset(Base):
    """Model for storing marketing assets (PDFs) with webhook data."""
    
    __tablename__ = "marketing_assets"
    
    # Primary key - UUID
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        server_default=func.uuid_generate_v4(),
    )
    
    # Asset identifier
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    
    # Original filename (before sequential renaming)
    original_filename: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    
    # Sequential number for file naming (001, 002, etc.)
    sequence_number: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        index=True,
    )
    
    # Storage URL (local path accessible via static mount)
    storage_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    
    # Job status
    status: Mapped[AssetStatus] = mapped_column(
        String(50),
        nullable=False,
        default=AssetStatus.UPLOADED,
        server_default=AssetStatus.UPLOADED,
    )
    
    # JSONB column for webhook callback data
    webhook_payload: Mapped[Optional[dict]] = mapped_column(
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
    
    # Relationship to ContentSnack
    snacks: Mapped[list["ContentSnack"]] = relationship(
        "ContentSnack",
        back_populates="asset",
        lazy="selectin",  # Async-compatible loading strategy
        cascade="all, delete-orphan",
    )
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<MarketingAsset(id={self.id}, filename={self.filename}, sequence_number={self.sequence_number}, status={self.status})>"

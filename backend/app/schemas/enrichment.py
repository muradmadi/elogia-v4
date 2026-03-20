"""Pydantic schemas for EnrichmentJob model."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# Base schema with common fields
class EnrichmentJobBase(BaseModel):
    """Base schema for EnrichmentJob."""
    
    job_id: UUID = Field(..., description="Unique identifier for the job")
    email: str = Field(..., min_length=1, max_length=255, description="Email address to enrich")
    status: str = Field("pending", description="Current status of the job")
    
    # JSONB payload fields
    payload_1: Optional[dict] = Field(None, description="First payload data")
    payload_2: Optional[dict] = Field(None, description="Second payload data")
    payload_3: Optional[dict] = Field(None, description="Third payload data")
    payload_4: Optional[dict] = Field(None, description="Fourth payload data")
    payload_5: Optional[dict] = Field(None, description="Fifth payload data")
    payload_6: Optional[dict] = Field(None, description="Sixth payload data")


# Schema for creating a new job
class EnrichmentJobCreate(EnrichmentJobBase):
    """Schema for creating a new EnrichmentJob."""
    
    model_config = ConfigDict(extra="forbid")


# Schema for updating an existing job
class EnrichmentJobUpdate(BaseModel):
    """Schema for updating an EnrichmentJob."""
    
    status: Optional[str] = Field(None, description="Updated status")
    payload_1: Optional[dict] = Field(None, description="Updated first payload")
    payload_2: Optional[dict] = Field(None, description="Updated second payload")
    payload_3: Optional[dict] = Field(None, description="Updated third payload")
    payload_4: Optional[dict] = Field(None, description="Updated fourth payload")
    payload_5: Optional[dict] = Field(None, description="Updated fifth payload")
    payload_6: Optional[dict] = Field(None, description="Updated sixth payload")
    
    model_config = ConfigDict(extra="forbid")


# Schema for reading a job (includes read-only fields)
class EnrichmentJobResponse(EnrichmentJobBase):
    """Schema for returning EnrichmentJob data."""
    
    id: UUID = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


# Schema for listing jobs with pagination
class EnrichmentJobListResponse(BaseModel):
    """Schema for paginated list of EnrichmentJobs."""
    
    items: list[EnrichmentJobResponse] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total number of jobs")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
    
    model_config = ConfigDict(from_attributes=True)


# Schema for job summary (frontend dropdown)
class JobSummary(BaseModel):
    """Schema for job summary in frontend dropdown."""
    
    job_id: UUID = Field(..., description="Unique identifier for the job")
    email: str = Field(..., min_length=1, max_length=255, description="Email address to enrich")
    status: str = Field(..., description="Current status of the job")
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


# Schema for consolidated payload (full job with all JSONB payloads)
class ConsolidatedPayload(BaseModel):
    """Schema for consolidated payload with all JSONB data."""
    
    id: UUID = Field(..., description="Unique identifier")
    job_id: UUID = Field(..., description="Unique identifier for the job")
    email: str = Field(..., min_length=1, max_length=255, description="Email address to enrich")
    status: str = Field(..., description="Current status of the job")
    
    # JSONB payload fields
    payload_1: Optional[dict] = Field(None, description="First payload data")
    payload_2: Optional[dict] = Field(None, description="Second payload data")
    payload_3: Optional[dict] = Field(None, description="Third payload data")
    payload_4: Optional[dict] = Field(None, description="Fourth payload data")
    payload_5: Optional[dict] = Field(None, description="Fifth payload data")
    payload_6: Optional[dict] = Field(None, description="Sixth payload data")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

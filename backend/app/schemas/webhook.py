"""Pydantic schemas for Clay webhook payloads."""
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# Payload types that Clay can send
ClayPayloadType = Literal[
    "person",
    "company",
    "profile",
    "products",
    "painpoints",
    "communication",
]


class ClayWebhookPayload(BaseModel):
    """Incoming Clay webhook payload schema."""
    
    job_id: UUID = Field(
        ...,
        description="Job identifier for the enrichment job",
    )
    
    email: str = Field(
        ...,
        description="Email address being enriched",
        min_length=1,
        max_length=255,
    )
    
    payload_type: ClayPayloadType = Field(
        ...,
        description="Type of payload being sent by Clay",
    )
    
    data: dict = Field(
        ...,
        description="Dynamic payload data from Clay",
    )
    
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )

"""Base schema for all Pydantic models with common configuration."""
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration for all Pydantic models.
    
    This provides a consistent configuration across all schema classes:
    - from_attributes=True: Allows ORM -> Pydantic conversion
    - populate_by_name=True: Allows field population by alias
    - extra="ignore": Allows alias mapping and ignores extra fields
    """
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="ignore",
    )
